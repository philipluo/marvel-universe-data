#!/usr/bin/env python3
"""
sync_to_local.py — 单向同步工具：将云端已有的数据同步到本地 Desktop。

读取 .env.local 连接本地 Neo4j，然后检查 scheduled_data/index.json
的 import_log.local，找出标记为 "pending" 或 "failed" 的内容（batches + fixed 文件）
并逐个执行到本地数据库。执行后更新 index.json。

幂等安全——所有语句是 MATCH...MERGE，重复执行无害。

用法：
    python3 scripts/import/sync_to_local.py            # 同步未同步内容
    python3 scripts/import/sync_to_local.py --status   # 只看差异，不执行
    python3 scripts/import/sync_to_local.py --force    # 全部重新跑一遍
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------- paths ----------
ROOT = Path(__file__).resolve().parents[2]
ENV_LOCAL = ROOT / ".env.local"
INDEX = ROOT / "scheduled_data" / "index.json"
FIXED_DIR = ROOT / "fixed"
SCHEDULED_DIR = ROOT / "scheduled_data"

# ---------- helpers ----------

def load_env_local() -> dict:
    """读取 .env.local 返回 dict"""
    env = {}
    for line in ENV_LOCAL.read_text().splitlines():
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
    """确保 import_log[target] 结构存在"""
    log = state.setdefault("import_log", {}).setdefault(target, {})
    log.setdefault("batches", {})
    log.setdefault("fixed", {})
    log.setdefault("last_ok", "")


def split_statements(text: str) -> list[str]:
    """拆分 Cypher 文本为独立语句"""
    text = re.sub(r"//.*", "", text)
    return [s.strip() + ";" for s in text.split(";") if s.strip()]


def execute_file(driver, path: Path, target_label: str) -> tuple[int, int]:
    """
    执行一个 .cypher 文件，返回 (成功数, 失败数).
    使用 target_label 做日志前缀。
    """
    content = path.read_text(encoding="utf-8")
    stmts = split_statements(content)
    ok = fail = 0
    with driver.session(database="universe") as session:
        for stmt in stmts:
            try:
                session.run(stmt).consume()
                ok += 1
            except Exception as e:
                fail += 1
                if fail <= 3:
                    print(f"      ❌ {str(e)[:80]}")
    return ok, fail


# ---------- main ----------

def compute_pending(state: dict, target: str) -> dict:
    """
    返回待同步的二维表：
    {
        "batches": [batch_num_str, ...],   # 已生成但未同步到 target 的批次
        "fixed": [filename, ...],          # 已修改但未同步的 fixed 文件
    }
    """
    log = state.get("import_log", {}).get(target, {})
    batch_status = log.get("batches", {})
    fixed_status = log.get("fixed", {})

    completed = state.get("completed_batches", [])

    # pending batches = completed 中状态不是 "ok" 的
    pending_batches = []
    for b in completed:
        if batch_status.get(b) != "ok":
            pending_batches.append(b)

    # pending fixed files = fixed/ 目录下核心关系文件，mtime 变或状态不是 "ok" 的
    tracked_fixed = {
        "relationships_movie_appearances.cypher",
        "data_corrections.cypher",
    }
    pending_fixed = []
    for fname in sorted(tracked_fixed):
        fpath = FIXED_DIR / fname
        if not fpath.exists():
            continue
        cur_mtime = datetime.fromtimestamp(fpath.stat().st_mtime).isoformat(timespec="seconds")
        last = fixed_status.get(fname, {})
        if isinstance(last, str):
            # 旧格式：直接是 "ok"（无 mtime 记录 → 已同步, 跳过）
            if last == "ok":
                continue
        elif isinstance(last, dict):
            if last.get("status") == "ok" and last.get("mtime") == cur_mtime:
                continue
        pending_fixed.append(fname)

    return {"batches": pending_batches, "fixed": pending_fixed}


def run_sync(target: str, driver, state: dict, force: bool = False):
    """
    执行同步到指定 target。force=True 则重新执行所有内容（幂等）。
    """
    log = state.setdefault("import_log", {}).setdefault(target, {})
    ensure_import_log(state, target)
    batch_status = log["batches"]
    fixed_status = log["fixed"]

    if force:
        # 把所有变成 pending
        for b in log["batches"]:
            log["batches"][b] = "pending"
        for f in log["fixed"]:
            log["fixed"][f] = "pending"

    pending = compute_pending(state, target)

    pending_batches = pending["batches"]
    pending_fixed = pending["fixed"]

    if not pending_batches and not pending_fixed:
        print(f"📭 {target}: 没有待同步内容")
        return

    total_ok = total_fail = 0

    # 1. fixed 文件（先跑，因为它们可能包含新关系类型定义）
    if pending_fixed:
        print(f"\n📁 {target}: 同步固定关系文件...")
        for fname in pending_fixed:
            fpath = FIXED_DIR / fname
            if not fpath.exists():
                print(f"  ⏭️  {fname} 不存在，跳过")
                continue
            cur_mtime = datetime.fromtimestamp(fpath.stat().st_mtime).isoformat(timespec="seconds")
            print(f"  📄 {fname}...", end=" ", flush=True)
            ok, fail = execute_file(driver, fpath, target)
            total_ok += ok
            total_fail += fail
            if fail == 0:
                # 新格式：存 mtime 和 status
                fixed_status[fname] = {"status": "ok", "mtime": cur_mtime}
                print(f"✅ {ok} 条")
            else:
                fixed_status[fname] = {"status": "failed", "mtime": cur_mtime}
                print(f"⚠️  {ok} 成功, {fail} 失败")

    # 2. batch 文件
    if pending_batches:
        print(f"\n📦 {target}: 同步批次...")
        # 按序号排序
        for b in sorted(pending_batches, key=int):
            batch_dir = SCHEDULED_DIR / f"batch_{int(b):03d}"
            if not batch_dir.exists():
                print(f"  ⏭️  批次 {b} 目录不存在: {batch_dir}")
                batch_status[b] = "failed"
                continue

            cypher_files = sorted(batch_dir.glob("*.cypher"))
            print(f"  📂 批次 {b} ({len(cypher_files)} 个文件)...")
            batch_ok = batch_fail = 0
            for fpath in cypher_files:
                ok, fail = execute_file(driver, fpath, target)
                batch_ok += ok
                batch_fail += fail
                label = f"    📄 {fpath.name}: {ok} 成功"
                if fail:
                    label += f", {fail} 失败"
                print(label)
            total_ok += batch_ok
            total_fail += batch_fail
            batch_status[b] = "ok" if batch_fail == 0 else "failed"

    # 3. 更新 last_ok
    if total_fail == 0 and (pending_batches or pending_fixed):
        log["last_ok"] = datetime.now().isoformat(timespec="seconds")

    write_index(state)
    print(f"\n📊 {target} 同步结果: {total_ok} 成功, {total_fail} 失败")


# ---------- CLI ----------

def print_status():
    """打印两个目标的状态汇总"""
    state = read_index()
    for target in ("cloud", "local"):
        ensure_import_log(state, target)
        pending = compute_pending(state, target)
        log = state["import_log"][target]
        last = log.get("last_ok", "从未")
        p_batch = pending["batches"]
        p_fixed = pending["fixed"]
        print(f"\n{'='*50}")
        print(f"  {target.upper()}: 上次同步 {last}")
        print(f"{'='*50}")
        if not p_batch and not p_fixed:
            print("  ✅ 全部同步完成")
        else:
            if p_batch:
                print(f"  📦 待同步批次: {', '.join(p_batch)}")
            if p_fixed:
                print(f"  📁 待同步文件: {', '.join(p_fixed)}")


def main():
    parser = argparse.ArgumentParser(description="同步数据到本地 Neo4j Desktop")
    parser.add_argument("--status", action="store_true", help="只看差异，不执行")
    parser.add_argument("--force", action="store_true", help="强制全部重新同步")
    args = parser.parse_args()

    # 状态模式
    if args.status:
        print_status()
        return

    # 读取状态
    state = read_index()
    ensure_import_log(state, "local")

    # 加载本地凭证
    if not ENV_LOCAL.exists():
        print(f"❌ .env.local 不存在: {ENV_LOCAL}")
        sys.exit(1)

    env = load_env_local()
    uri = env.get("NEO4J_URI")
    user = env.get("NEO4J_USER")
    password = env.get("NEO4J_PASSWORD")

    if not password:
        print("❌ 本地配置不完整")
        sys.exit(1)

    # 连接本地
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print(f"✅ 本地连接成功: {uri}")
    except Exception as e:
        print(f"❌ 本地连接失败: {e}")
        sys.exit(1)

    # 执行同步
    try:
        run_sync("local", driver, state, force=args.force)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
