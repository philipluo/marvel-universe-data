#!/usr/bin/env python3
"""
run.py — 统一数据收集与入库入口。

执行流程：
  1. 生成下一批数据文件（或按 --batch 指定）
  2. 优先导入云端（读取 .env），不通则记录 failed
  3. 同步本地 Desktop（读取 .env.local），不通则记录 failed
  4. 每次自动发现未入库内容重试

用法：
    python3 scripts/collector/run.py              # 下一批 + 云优先 + fallback
    python3 scripts/collector/run.py --batch 3    # 指定批次
    python3 scripts/collector/run.py --retry      # 不生成新批次，只重试未入库内容
    python3 scripts/collector/run.py --generate-only  # 只生成文件，不导数据库
    python3 scripts/collector/run.py --list-batches   # 列出所有批次定义
    python3 scripts/collector/run.py --status     # 查看同步状态
    python3 scripts/collector/run.py --report     # 只更新 REPORT.md
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------- 路径 ----------
ROOT = Path(__file__).resolve().parents[2]
FIXED_DIR = ROOT / "fixed"
SCHEDULED_DIR = ROOT / "scheduled_data"
INDEX = SCHEDULED_DIR / "index.json"
ENV_CLOUD = ROOT / ".env"
ENV_LOCAL = ROOT / ".env.local"

# 确保可 import 同级模块
sys.path.insert(0, str(ROOT / "scripts" / "collector"))
from collector_helper import (  # noqa: E402
    get_batch_state, save_batch_state, generate_batch, print_status,
)
from data_definitions import BATCHES  # noqa: E402


# ---------- 工具函数 ----------

def load_env(path: Path) -> dict:
    """读取 .env 文件返回 dict"""
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip("\"").strip("'")
    return env


def read_index() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {"completed_batches": [], "import_log": {}}


def write_index(state: dict):
    INDEX.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_import_log(state: dict, target: str):
    """确保 import_log[target] 结构完整"""
    log = state.setdefault("import_log", {}).setdefault(target, {})
    log.setdefault("batches", {})
    log.setdefault("fixed", {})
    log.setdefault("last_ok", "")


def split_statements(text: str) -> list[str]:
    text = re.sub(r"//.*", "", text)
    return [s.strip() + ";" for s in text.split(";") if s.strip()]


def try_connect(uri: str, user: str, password: str):
    """尝试连接 Neo4j，成功返回 driver，失败返回 None"""
    try:
        from neo4j import GraphDatabase
        d = GraphDatabase.driver(uri, auth=(user, password))
        d.verify_connectivity()
        return d
    except Exception:
        return None


def execute_file(driver, path: Path) -> tuple[int, int]:
    """执行一个 .cypher 文件，返回 (成功数, 失败数)"""
    content = path.read_text(encoding="utf-8")
    stmts = split_statements(content)
    ok = fail = 0
    with driver.session(database="universe") as session:
        for stmt in stmts:
            try:
                session.run(stmt).consume()
                ok += 1
            except Exception:
                fail += 1
    return ok, fail


# ---------- 核心同步逻辑 ----------

def get_pending_items(state: dict, target: str, force: bool = False) -> dict:
    """
    返回 target 待同步的内容列表.
    force=True 则返回全部（包括已 ok 的，用于重跑）。
    """
    log = state.get("import_log", {}).get(target, {})
    completed = state.get("completed_batches", [])

    # pending batches
    all_batches = set(completed)
    if force:
        # force 时也包含已完成但在 import_log 中无记录的批次
        logged_batches = set(log.get("batches", {}).keys())
        pending = sorted(all_batches | logged_batches, key=int)
    else:
        batch_status = log.get("batches", {})
        pending = sorted([b for b in completed if batch_status.get(b) != "ok"], key=int)

    # pending fixed
    tracked = ["relationships_movie_appearances.cypher", "data_corrections.cypher"]
    fixed_status = log.get("fixed", {})
    pending_fixed = []
    for fname in tracked:
        fpath = FIXED_DIR / fname
        if not fpath.exists():
            continue
        cur_mtime = datetime.fromtimestamp(fpath.stat().st_mtime).isoformat(timespec="seconds")
        if force:
            pending_fixed.append(fname)
            continue
        last = fixed_status.get(fname)
        if last == "ok":
            continue
        if isinstance(last, dict) and last.get("status") == "ok":
            if last.get("mtime") == cur_mtime:
                continue
        pending_fixed.append(fname)

    return {"batches": pending, "fixed": pending_fixed}


def sync_target(target: str, driver, state: dict, force: bool = False):
    """同步所有待同步内容到 target，更新 state 但不写盘"""
    log = state.setdefault("import_log", {}).setdefault(target, {})
    ensure_import_log(state, target)
    batch_status = log["batches"]
    fixed_status = log["fixed"]

    pending = get_pending_items(state, target, force=force)
    pending_batches = pending["batches"]
    pending_fixed = pending["fixed"]

    if not pending_batches and not pending_fixed:
        return 0, 0

    total_ok = total_fail = 0

    # 1) fixed 文件
    for fname in pending_fixed:
        fpath = FIXED_DIR / fname
        if not fpath.exists():
            continue
        cur_mtime = datetime.fromtimestamp(fpath.stat().st_mtime).isoformat(timespec="seconds")
        ok, fail = execute_file(driver, fpath)
        total_ok += ok
        total_fail += fail
        fixed_status[fname] = {
            "status": "ok" if fail == 0 else "failed",
            "mtime": cur_mtime,
        }

    # 2) batch
    for b in pending_batches:
        batch_dir = SCHEDULED_DIR / f"batch_{int(b):03d}"
        if not batch_dir.exists():
            batch_status[b] = "failed"
            continue
        batch_ok = batch_fail = 0
        for fpath in sorted(batch_dir.glob("*.cypher")):
            ok, fail = execute_file(driver, fpath)
            batch_ok += ok
            batch_fail += fail
        total_ok += batch_ok
        total_fail += batch_fail
        batch_status[b] = "ok" if batch_fail == 0 else "failed"

    if total_fail == 0 and (pending_batches or pending_fixed):
        log["last_ok"] = datetime.now().isoformat(timespec="seconds")

    return total_ok, total_fail


def do_sync(state: dict, target: str, env: dict, label: str, force: bool = False) -> bool:
    """尝试同步一个目标，返回是否被同步（无论成败）"""
    ensurer = {"cloud": "云端", "local": "本地"}
    cn = ensurer.get(target, target)
    uri = env.get("NEO4J_URI")
    user = env.get("NEO4J_USER")
    password = env.get("NEO4J_PASSWORD")

    if not password:
        print(f"  ⏭️  {cn}: 无配置")
        return False

    driver = try_connect(uri, user, password)
    if driver is None:
        print(f"  ❌ {cn}: 无法连接")
        # 将待同步内容统一标为 failed
        pending = get_pending_items(state, target)
        for b in pending.get("batches", []):
            state["import_log"][target]["batches"][b] = "failed"
        for f in pending.get("fixed", []):
            state["import_log"][target]["fixed"][f] = {"status": "failed", "mtime": ""}
        return False

    try:
        print(f"  ✅ {cn}: 连接成功")
        ok, fail = sync_target(target, driver, state, force=force)
        if ok or fail:
            print(f"  📊 {cn}: {ok} 成功, {fail} 失败")
        else:
            print(f"  📭 {cn}: 无需同步")
        return True
    finally:
        driver.close()


# ---------- CLI ----------

def cmd_status():
    """打印同步状态"""
    state = read_index()
    for target, label in [("cloud", "云端"), ("local", "本地")]:
        ensure_import_log(state, target)
        log = state["import_log"][target]
        last = log.get("last_ok", "从未")
        pending = get_pending_items(state, target)
        print(f"\n{'='*50}")
        print(f"  {label}（{target}）: 上次同步 {last}")
        print(f"{'='*50}")
        if not pending["batches"] and not pending["fixed"]:
            print("  ✅ 全部同步完成")
        else:
            if pending["fixed"]:
                print(f"  📁 待同步文件: {', '.join(pending['fixed'])}")
            if pending["batches"]:
                print(f"  📦 待同步批次: {', '.join(pending['batches'])}")


def cmd_run(batch_num: int = None, force: bool = False, sync: bool = True):
    """
    生成批（如需要）→ 同步 cloud → 同步 local。
    batch_num=None 则自动下一批。sync=False 只生成不同步。
    """
    state = read_index()

    # ---- 1. 生成批次（如果有新批次需要生成） ----
    if batch_num or not force:
        # 判断是否有批次需要生成
        completed = state.get("completed_batches", [])
        if batch_num:
            b = batch_num
        else:
            b = len(completed) + 1

        if str(b) not in completed:
            if b > len(BATCHES):
                print(f"🎉 所有 {len(BATCHES)} 批都已完成，无需生成")
            else:
                print(f"\n{'='*60}")
                print(f"  生成批次 {b}: {BATCHES[b-1]['name']}")
                print(f"{'='*60}")
                generate_batch(b)
                # 重新读取 state（generate_batch 内部 save_batch_state 了）
                state = read_index()
                # 为新批次初始化 import_log 状态
                for target in ("cloud", "local"):
                    ensure_import_log(state, target)
                    state["import_log"][target]["batches"][str(b)] = "pending"
                write_index(state)
        else:
            print(f"⏭️  批次 {b} 已生成过")

    # ---- 2. 重新读状态（可能刚写入过） ----
    state = read_index()

    # ---- 3. 同步云端（sync=False 时跳过） ----
    if sync:
        print(f"\n{'='*60}")
        print("  同步云端（主数据库）")
        print(f"{'='*60}")
        if ENV_CLOUD.exists():
            do_sync(state, "cloud", load_env(ENV_CLOUD), "云端", force=force)
        else:
            print("  ⏭️  云端: .env 不存在")

        # ---- 4. 同步本地 ----
        print(f"\n{'='*60}")
        print("  同步本地 Desktop")
        print(f"{'='*60}")
        if ENV_LOCAL.exists():
            do_sync(state, "local", load_env(ENV_LOCAL), "本地", force=force)
        else:
            print("  ⏭️  本地: .env.local 不存在")

        # ---- 5. 持久化 ----
        write_index(state)
        print(f"\n{'='*60}")
        print("  ✅ 完成")
        print(f"{'='*60}")
    else:
        print("\n⏭️  --generate-only 模式：跳过数据库同步")

    # ---- 6. 更新 REPORT.md ----
    print("\n📝 更新报告...")
    try:
        from collector_helper import generate_report
        generate_report()
        print("✅ REPORT.md 已更新")
    except Exception as e:
        print(f"⚠️  报告生成失败: {e}")


def cmd_report():
    """仅更新 REPORT.md"""
    print("📝 生成 REPORT.md...")
    try:
        from collector_helper import generate_report
        generate_report()
        print("✅ REPORT.md 已更新")
    except Exception as e:
        print(f"⚠️  报告生成失败: {e}")


def cmd_list_batches():
    """列出所有定义的批次"""
    print(f"\n共 {len(BATCHES)} 个批次:\n")
    for i, batch in enumerate(BATCHES, 1):
        chars = len(batch.get("characters", []))
        rels = len(batch.get("relationships", []))
        teams = len(batch.get("teams", []))
        print(f"  批次 {i}: {batch['name']}")
        print(f"        {chars} 角色, {teams} 团队, {rels} 关系")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="漫威数据收集入口 — 生成 + 云端优先 + 本地同步"
    )
    parser.add_argument("--batch", type=int, help="指定批次号")
    parser.add_argument("--retry", action="store_true",
                        help="不生成新批，只重试未入库内容")
    parser.add_argument("--generate-only", action="store_true",
                        help="只生成文件，不连接数据库")
    parser.add_argument("--force", action="store_true",
                        help="强制全部重新同步（幂等）")
    parser.add_argument("--list-batches", action="store_true", help="列出所有批次定义")
    parser.add_argument("--status", action="store_true", help="查看同步状态")
    parser.add_argument("--report", action="store_true", help="仅更新 REPORT.md")

    args = parser.parse_args()

    # 无需联网的子命令
    if args.status:
        cmd_status()
        return
    if args.report:
        cmd_report()
        return
    if args.list_batches:
        cmd_list_batches()
        return

    # 仅生成文件，不连数据库
    if args.generate_only:
        cmd_run(batch_num=args.batch, sync=False)
        return

    # 重试模式：不生成新批，只同步 pending
    if args.retry:
        cmd_run(batch_num=None, force=args.force)
        return

    # 指定批次
    if args.batch:
        cmd_run(batch_num=args.batch, force=args.force)
        return

    # 默认：自动下一批
    cmd_run(batch_num=None, force=args.force)


if __name__ == "__main__":
    main()
