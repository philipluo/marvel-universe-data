#!/usr/bin/env python3
"""
run_batch.py — 漫威数据收集器 CLI 入口

用于 Hermes/cron 定时自动收集漫威数据，生成正确格式的 Cypher 文件。

用法：
    python scripts/collector/run_batch.py                  # 生成下一批
    python scripts/collector/run_batch.py --status          # 查看进度
    python scripts/collector/run_batch.py --batch 2         # 生成指定批次
    python scripts/collector/run_batch.py --import          # 生成后导入 Neo4j
    python scripts/collector/run_batch.py --import-only     # 只导入未导入批次
    python scripts/collector/run_batch.py --list-batches    # 列出所有批次
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 添加上级目录到 path 以便引用 data_definitions (当从 scripts/ 根目录运行时)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from collector_helper import (
    ROOT, FIXED_DIR, SCHEDULED_DIR,
    escape_value,
    get_all_existing_entities,
    get_batch_state,
    save_batch_state,
    get_next_ids,
    parse_entity_statement,
    scan_directory,
    validate_batch_dir,
    write_batch_files,
    scan_used_var_ids,
    build_relationship_statement,
    generate_report,
)
from data_definitions import BATCHES


# ============================================================
# 核心逻辑：生成批次
# ============================================================

def generate_batch(batch_index: int, import_after: bool = False) -> bool:
    """
    生成第 batch_index 批数据（从 1 开始）。
    返回 True 表示生成了新数据，False 表示跳过。
    """
    if batch_index < 1 or batch_index > len(BATCHES):
        print(f"❌ 批次号无效: {batch_index}（有效范围 1-{len(BATCHES)}）")
        return False

    batch_def = BATCHES[batch_index - 1]
    batch_name = batch_def["name"]

    # 检查是否已生成
    state = get_batch_state()
    if str(batch_index) in state.get("completed_batches", []):
        print(f"⏭️  批次 {batch_index}（{batch_name}）已生成过，跳过")
        return False

    print(f"\n{'='*60}")
    print(f"  批次 {batch_index}: {batch_name}")
    print(f"{'='*60}")

    # 扫描已有实体用于去重
    existing = get_all_existing_entities()
    next_ids = get_next_ids(force_refresh=True)

    # 分配变量 ID
    id_counters = {
        "c": next_ids.get("c", 984),
        "t": next_ids.get("t", 17),
        "l": next_ids.get("l", 34),
        "m": next_ids.get("m", 30),
        "e": next_ids.get("e", 21),
        "i": next_ids.get("i", 215),
    }

    new_entities = []     # 本批新增实体
    skipped_entities = 0
    entity_var_map: dict[str, str] = {}  # name_en -> var 引用

    # --- 处理角色 ---
    for char_def in batch_def.get("characters", []):
        name_en = char_def.get("name_en", "")
        if not name_en:
            continue
        # 去重检查
        existing_var = existing.get("Character", {}).get(name_en)
        if existing_var:
            print(f"  ⏭️  角色已存在: {name_en} (var: {existing_var})")
            entity_var_map[name_en] = existing_var
            skipped_entities += 1
            continue

        var = f"c{id_counters['c']}"
        id_counters["c"] += 1
        entity_var_map[name_en] = var

        new_entities.append({
            "var": var,
            "label": "Character",
            "props": dict(char_def),
        })
        existing.setdefault("Character", {})[name_en] = var
        print(f"  ✅ 新角色: {var} → {name_en} ({char_def.get('name', '')})")

    # --- 处理团队 ---
    for team_def in batch_def.get("teams", []):
        name_en = team_def.get("name_en", "")
        if not name_en:
            continue
        existing_var = existing.get("Team", {}).get(name_en)
        if existing_var:
            print(f"  ⏭️  团队已存在: {name_en} (var: {existing_var})")
            entity_var_map[name_en] = existing_var
            skipped_entities += 1
            continue

        var = f"t{id_counters['t']}"
        id_counters["t"] += 1
        entity_var_map[name_en] = var

        new_entities.append({
            "var": var,
            "label": "Team",
            "props": dict(team_def),
        })
        existing.setdefault("Team", {})[name_en] = var
        print(f"  ✅ 新团队: {var} → {name_en} ({team_def.get('name', '')})")

    # --- 处理地点 ---
    for loc_def in batch_def.get("locations", []):
        name = loc_def.get("name", "")
        if not name:
            continue
        existing_var = existing.get("Location", {}).get(name)
        if existing_var:
            print(f"  ⏭️  地点已存在: {name} (var: {existing_var})")
            entity_var_map[name] = existing_var
            skipped_entities += 1
            continue

        var = f"l{id_counters['l']}"
        id_counters["l"] += 1
        entity_var_map[name] = var

        new_entities.append({
            "var": var,
            "label": "Location",
            "props": dict(loc_def),
        })
        existing.setdefault("Location", {})[name] = var
        print(f"  ✅ 新地点: {var} → {name}")

    # --- 处理电影 ---
    for movie_def in batch_def.get("movies", []):
        title = movie_def.get("title", "")
        if not title:
            continue
        existing_var = existing.get("Movie", {}).get(title)
        if existing_var:
            print(f"  ⏭️  电影已存在: {title} (var: {existing_var})")
            entity_var_map[title] = existing_var
            skipped_entities += 1
            continue

        var = f"m{id_counters['m']}"
        id_counters["m"] += 1
        entity_var_map[title] = var

        new_entities.append({
            "var": var,
            "label": "Movie",
            "props": dict(movie_def),
        })
        existing.setdefault("Movie", {})[title] = var
        print(f"  ✅ 新电影: {var} → {title}")

    # --- 处理事件 ---
    for event_def in batch_def.get("events", []):
        event_name = event_def.get("event_name", "")
        if not event_name:
            continue
        existing_var = existing.get("Event", {}).get(event_name)
        if existing_var:
            print(f"  ⏭️  事件已存在: {event_name} (var: {existing_var})")
            entity_var_map[event_name] = existing_var
            skipped_entities += 1
            continue

        var = f"e{id_counters['e']}"
        id_counters["e"] += 1
        entity_var_map[event_name] = var

        new_entities.append({
            "var": var,
            "label": "Event",
            "props": dict(event_def),
        })
        existing.setdefault("Event", {})[event_name] = var
        print(f"  ✅ 新事件: {var} → {event_name}")

    # --- 处理物品 ---
    for item_def in batch_def.get("items", []):
        item_key = item_def.get("item_name", item_def.get("name", ""))
        if not item_key:
            continue
        existing_var = existing.get("Item", {}).get(item_key)
        if existing_var:
            print(f"  ⏭️  物品已存在: {item_key} (var: {existing_var})")
            entity_var_map[item_key] = existing_var
            skipped_entities += 1
            continue

        var = f"i{id_counters['i']}"
        id_counters["i"] += 1
        entity_var_map[item_key] = var

        new_entities.append({
            "var": var,
            "label": "Item",
            "props": dict(item_def),
        })
        existing.setdefault("Item", {})[item_key] = var
        print(f"  ✅ 新物品: {var} → {item_key}")

    # --- 处理关系 ---
    new_relationships = []
    skipped_rels = 0
    for rel_def in batch_def.get("relationships", []):
        src_name, src_label, rel_type, tgt_name, tgt_label = rel_def[:5]
        bidirectional = rel_def[5] if len(rel_def) > 5 else False

        # 查找源和目标实体 ID
        src_var = existing.get(src_label, {}).get(src_name)
        tgt_var = existing.get(tgt_label, {}).get(tgt_name)

        if not src_var:
            print(f"  ⚠️  关系源未找到: {src_name} ({src_label})")
            skipped_rels += 1
            continue
        if not tgt_var:
            print(f"  ⚠️  关系目标未找到: {tgt_name} ({tgt_label})")
            skipped_rels += 1
            continue

        stmts = build_relationship_statement(
            src_var, src_label, _find_props(existing, src_name, src_label),
            rel_type,
            tgt_var, tgt_label, _find_props(existing, tgt_name, tgt_label),
            bidirectional,
        )
        new_relationships.append(stmts)

    # --- 检查是否有新数据 ---
    if not new_entities and not new_relationships:
        print(f"\n📭 批次 {batch_index} 没有新增数据（所有实体已存在）")
        # 标记为已完成
        state.setdefault("completed_batches", []).append(str(batch_index))
        save_batch_state(state)
        return False

    # --- 写入文件 ---
    batch_dir = write_batch_files(batch_index, new_entities, new_relationships)
    print(f"\n📁 写入: {batch_dir}")

    # --- 验证 ---
    errors = validate_batch_dir(batch_dir)
    if errors:
        print("\n⚠️  验证发现以下问题:")
        for err in errors:
            print(f"  {err}")
        # 不阻止写入，但提示
    else:
        print("✅ 格式验证通过")

    # --- 更新状态 ---
    state["latest_batch"] = batch_index
    state.setdefault("completed_batches", [])
    if str(batch_index) not in state["completed_batches"]:
        state["completed_batches"].append(str(batch_index))
    state["total_entities_added"] = state.get("total_entities_added", 0) + len(new_entities)
    state["next_ids"] = {
        "c": id_counters["c"],
        "t": id_counters["t"],
        "l": id_counters["l"],
        "m": id_counters["m"],
        "e": id_counters["e"],
        "i": id_counters["i"],
    }
    save_batch_state(state)

    print(f"\n📊 批次统计:")
    print(f"  新增实体: {len(new_entities)}")
    print(f"  新增关系: {len(new_relationships)}")
    print(f"  跳过实体: {skipped_entities}")
    print(f"  跳过关系: {skipped_rels}")
    print(f"  累计实体: {state['total_entities_added']}")

    # --- 可选：导入 Neo4j ---
    if import_after:
        import_batch_to_neo4j(batch_index, batch_dir)

    # --- 生成/更新报告 ---
    print("\n📝 更新报告...")
    try:
        generate_report()
        print("✅ REPORT.md 已更新")
    except Exception as e:
        print(f"⚠️ 报告生成失败: {e}")

    return True


def _find_props(existing: dict, name: str, label: str) -> dict:
    """
    返回最小的 props 字典，使 build_match_clause 能生成正确的 MATCH 子句。
    不同实体类型使用不同的匹配字段：
      Character/Team → name_en
      Movie          → title
      Event          → event_name
      Item           → item_name (fallback: name)
      Location       → name
    """
    if label in ("Character", "Team"):
        return {"name_en": name}
    elif label == "Movie":
        return {"title": name}
    elif label == "Event":
        return {"event_name": name}
    elif label == "Item":
        return {"item_name": name}
    else:
        return {"name": name}


# ============================================================
# 导入 Neo4j
# ============================================================

def import_batch_to_neo4j(batch_index: int, batch_dir: Path = None):
    """
    将指定批次导入本地 Neo4j。
    使用 .env 配置连接，不删除已有数据（MERGE 幂等）。
    """
    if batch_dir is None:
        batch_dir = SCHEDULED_DIR / f"batch_{batch_index:03d}"

    if not batch_dir.exists():
        print(f"❌ 批次目录不存在: {batch_dir}")
        return False

    # 加载 .env
    env_path = ROOT / ".env"
    if not env_path.exists():
        print(f"❌ .env 文件不存在: {env_path}")
        return False

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    uri = os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE")

    if not password:
        print("❌ NEO4J_PASSWORD 未在 .env 中设置")
        return False

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("❌ neo4j 驱动未安装，请执行: pip install neo4j")
        return False

    print(f"\n🔌 连接 Neo4j: {uri}  DB={database or '(default)'}")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        driver.verify_connectivity()
        print("✅ 连接成功")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

    # 读取并执行所有 .cypher 文件
    cypher_files = sorted(batch_dir.glob("*.cypher"))
    total_stmts = 0
    success = 0
    failed = 0

    for fpath in cypher_files:
        content = fpath.read_text(encoding="utf-8")
        # 分割语句（按分号分割，支持多行 MATCH...MERGE 组合）
        raw_stmts = content.split(";")
        stmts = []
        for chunk in raw_stmts:
            chunk = chunk.strip()
            if not chunk:
                continue
            # 过滤掉只有注释的行
            lines = [l for l in chunk.split("\n") if l.strip() and not l.strip().startswith("//")]
            if lines:
                stmts.append("\n".join(lines) + ";")

        if not stmts:
            continue

        print(f"\n  📄 {fpath.name}: {len(stmts)} 条语句")
        with driver.session(database=database) as session:
            for i, stmt in enumerate(stmts, 1):
                try:
                    session.run(stmt).consume()
                    success += 1
                except Exception as e:
                    failed += 1
                    if failed <= 3:
                        print(f"    ❌ 第{i}条失败: {str(e)[:120]}")
        total_stmts += len(stmts)

    driver.close()

    print(f"\n📊 导入结果: {success} 成功, {failed} 失败 (共 {total_stmts} 条)")

    # 验证
    print("\n🔍 导入后验证:")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=database) as session:
        result = session.run(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label"
        )
        rows = [r.data() for r in result]
        total_nodes = sum(r["count"] for r in rows)
        print(f"  节点总数: {total_nodes}")
        for r in rows:
            print(f"    {r['label']}: {r['count']}")

        result = session.run(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type"
        )
        rows = [r.data() for r in result]
        total_rels = sum(r["count"] for r in rows)
        print(f"  关系总数: {total_rels}")
        for r in rows:
            print(f"    {r['type']}: {r['count']}")
    driver.close()

    return failed == 0


# ============================================================
# 状态报告
# ============================================================

def print_status():
    """打印收集进度"""
    state = get_batch_state()
    existing = get_all_existing_entities()

    # 从 fixed/ 统计已有数据
    fixed = scan_directory(FIXED_DIR)
    scheduled = scan_directory(SCHEDULED_DIR)

    print("\n" + "=" * 60)
    print("  漫威数据收集进度")
    print("=" * 60)

    total_fixed = sum(len(v) for v in fixed.values())
    total_scheduled = sum(len(v) for v in scheduled.values())

    print(f"\n📁 fixed/（已导入 Neo4j）: {total_fixed} 个实体")
    print(f"📁 scheduled_data/: {total_scheduled} 个实体")

    print(f"\n📍 节点分布:")
    label_names = {
        "Character": "角色", "Team": "团队", "Location": "地点",
        "Movie": "电影", "Event": "事件", "Item": "物品",
    }
    grand_total = 0
    for label, cn in label_names.items():
        f_count = len(fixed.get(label, {}))
        s_count = len(scheduled.get(label, {}))
        total = f_count + s_count
        if total > 0:
            grand_total += total
            print(f"  {cn}: {total} (fixed: {f_count}, scheduled: {s_count})")
    print(f"\n  总计: {grand_total} 个实体")

    print(f"\n📅 批次进度:")
    completed = state.get("completed_batches", [])
    for i in range(1, len(BATCHES) + 1):
        mark = "✅" if str(i) in completed else "⏳"
        print(f"  {mark} 批次 {i}: {BATCHES[i - 1]['name']}")

    if completed:
        print(f"\n  已完成: {len(completed)}/{len(BATCHES)} 批")
        print(f"  累计新增实体: {state.get('total_entities_added', 0)}")

    print(f"\n📌 下一批可用 ID:")
    next_ids = get_next_ids()
    for prefix, label in [("c", "角色"), ("t", "团队"), ("l", "地点"),
                           ("m", "电影"), ("e", "事件"), ("i", "物品")]:
        print(f"  {prefix}: {next_ids.get(prefix, '?')}（下一个{label}ID）")


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="漫威数据收集器 — 生成正确格式的 Cypher 数据文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/collector/run_batch.py               # 生成下一批
  python scripts/collector/run_batch.py --status       # 查看进度
  python scripts/collector/run_batch.py --batch 2      # 生成第 2 批
  python scripts/collector/run_batch.py --import       # 生成下一批并导入 Neo4j
  python scripts/collector/run_batch.py --import-only  # 导入所有未导入批次
  python scripts/collector/run_batch.py --list-batches # 列出所有批次
        """
    )
    parser.add_argument("--status", action="store_true", help="查看收集进度")
    parser.add_argument("--batch", type=int, help="指定生成批次号")
    parser.add_argument("--import", dest="import_after", action="store_true",
                        help="生成后导入 Neo4j")
    parser.add_argument("--import-only", action="store_true",
                        help="仅导入未导入的批次")
    parser.add_argument("--list-batches", action="store_true", help="列出所有批次")
    parser.add_argument("--report", action="store_true", help="仅更新 REPORT.md 总表")

    if len(sys.argv) == 1:
        # 无参数 = 自动生成下一批
        state = get_batch_state()
        next_batch = len(state.get("completed_batches", [])) + 1
        if next_batch > len(BATCHES):
            print("🎉 所有批次已完成！使用 --status 查看进度")
            return
        generate_batch(next_batch)
        return

    args = parser.parse_args()

    if args.list_batches:
        print(f"\n共 {len(BATCHES)} 个批次:\n")
        for i, batch in enumerate(BATCHES, 1):
            chars = len(batch.get("characters", []))
            rels = len(batch.get("relationships", []))
            teams = len(batch.get("teams", []))
            print(f"  批次 {i}: {batch['name']}")
            print(f"        {chars} 角色, {teams} 团队, {rels} 关系")
        return

    if args.report:
        print("📝 生成 REPORT.md...")
        try:
            report = generate_report()
            print(report[:500])
            print("...")
            print(f"✅ REPORT.md 已更新")
        except Exception as e:
            print(f"⚠️ 报告生成失败: {e}")
            import traceback
            traceback.print_exc()
        return

    if args.status:
        print_status()
        return

    if args.import_only:
        state = get_batch_state()
        completed = state.get("completed_batches", [])
        imported_count = 0
        for batch_id in completed:
            batch_num = int(batch_id)
            batch_dir = SCHEDULED_DIR / f"batch_{batch_num:03d}"
            if batch_dir.exists():
                print(f"\n导入批次 {batch_id}...")
                if import_batch_to_neo4j(batch_num, batch_dir):
                    imported_count += 1
        print(f"\n✅ 已导入 {imported_count} 个批次")
        # 生成报告
        print("\n📝 更新报告...")
        try:
            generate_report()
            print("✅ REPORT.md 已更新")
        except Exception as e:
            print(f"⚠️ 报告生成失败: {e}")
        return

    if args.batch:
        generate_batch(args.batch, import_after=args.import_after)
        return

    # 默认：自动下一批
    state = get_batch_state()
    next_batch = len(state.get("completed_batches", [])) + 1
    if next_batch > len(BATCHES):
        print("🎉 所有批次已完成！使用 --report 更新总表")
        return
    generate_batch(next_batch, import_after=args.import_after)


if __name__ == "__main__":
    main()
