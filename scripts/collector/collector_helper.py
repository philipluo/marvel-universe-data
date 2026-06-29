#!/usr/bin/env python3
"""
collector_helper.py — 漫威数据收集工具库

核心功能：
- 扫描 fixed/ + scheduled_data/ 已有数据用于去重
- 管理变量 ID 分配（cN, tN, lN, mN, eN, iN）
- 生成正确格式的 Cypher MERGE 语句
- 验证 Cypher 语法
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# data_definitions 在同目录，直接引用
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_definitions import BATCHES  # noqa: E402

# ============================================================
# 路径
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
FIXED_DIR = ROOT / "fixed"
SCHEDULED_DIR = ROOT / "scheduled_data"
INDEX_FILE = SCHEDULED_DIR / "index.json"

# 关系标签（统一中文）
REL_LABELS = {
    "MEMBER_OF": "成员",
    "成员": "成员",
    "ENEMY_OF": "敌人",
    "敌人": "敌人",
    "ALLY_OF": "盟友",
    "盟友": "盟友",
    "RELATIVE_OF": "亲属",
    "亲属": "亲属",
    "FROM": "来自",
    "来自": "来自",
    "USES": "使用",
    "使用": "使用",
    "HERALD_OF": "使者",
    "使者": "使者",
    "APPEARS_IN": "出演",
    "出演": "出演",
}

# 双向关系类型（自动生成反向）
BIDIRECTIONAL_REL_TYPES = {"ENEMY_OF", "敌人", "ALLY_OF", "盟友"}

# ============================================================
# 实体扫描与去重
# ============================================================

def parse_entity_statement(stmt: str) -> dict | None:
    """解析单条 MERGE 语句，返回 {var, label, props} 或 None"""
    # 处理跨行语句
    stmt_clean = stmt.replace("\n", " ").replace("\r", " ").strip()
    m = re.match(
        r'MERGE\s+\((\w+):(\w+)\s*\{(.*)\}\)\s*;?\s*$',
        stmt_clean, re.DOTALL
    )
    if not m:
        return None
    var, label, props_str = m.group(1), m.group(2), m.group(3)
    props = _parse_props(props_str)
    return {"var": var, "label": label, "props": props}


def _parse_props(props_str: str) -> dict[str, str]:
    """解析 Cypher 属性字符串为字典"""
    props: dict[str, str] = {}
    i = 0
    length = len(props_str)
    while i < length:
        while i < length and props_str[i] in " \t\n\r,":
            i += 1
        if i >= length:
            break
        km = re.match(r'(\w+):\s*', props_str[i:])
        if not km:
            break
        key = km.group(1)
        i += km.end()
        if i >= length:
            break
        if props_str[i] == '"':
            i += 1
            val_chars = []
            while i < length:
                if props_str[i] == '\\' and i + 1 < length:
                    val_chars.append(props_str[i + 1])
                    i += 2
                elif props_str[i] == '"':
                    i += 1
                    break
                else:
                    val_chars.append(props_str[i])
                    i += 1
            props[key] = "".join(val_chars)
        else:
            vm = re.match(r'([^,}\n]+)', props_str[i:])
            if vm:
                props[key] = vm.group(1).strip()
                i += vm.end()
    return props


def get_entity_key(label: str, props: dict) -> str | None:
    """获取实体的唯一标识字符串（用于去重）"""
    if label in ("Character", "Team"):
        return props.get("name_en")
    elif label == "Movie":
        return props.get("title")
    elif label == "Event":
        return props.get("event_name")
    elif label == "Item":
        return props.get("item_name") or props.get("name")
    elif label == "Location":
        return props.get("name")
    return props.get("name")


def scan_directory(directory: Path) -> dict[str, dict[str, str]]:
    """
    扫描目录下所有 .cypher 文件，返回 {label: {entity_key: var_name}}
    """
    result: dict[str, dict[str, str]] = {}
    if not directory.exists():
        return result
    for fpath in sorted(directory.rglob("*.cypher")):
        content = fpath.read_text(encoding="utf-8")
        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                continue
            parsed = parse_entity_statement(stripped)
            if parsed:
                label = parsed["label"]
                props = parsed["props"]
                key = get_entity_key(label, props)
                if key:
                    result.setdefault(label, {})[key] = parsed["var"]
    return result


def scan_used_var_ids(directory: Path) -> dict[str, set[int]]:
    """扫描已用变量序号，返回 {前缀: {序号集合}}"""
    used: dict[str, set[int]] = {}
    if not directory.exists():
        return used
    for fpath in sorted(directory.rglob("*.cypher")):
        content = fpath.read_text(encoding="utf-8")
        for m in re.finditer(r'\b([ctlmei])(\d+)\s*:', content):
            prefix, num = m.group(1), int(m.group(2))
            used.setdefault(prefix, set()).add(num)
    return used


def get_all_existing_entities() -> dict[str, dict[str, str]]:
    """扫描 fixed/ + scheduled_data/ 所有已有实体"""
    result = scan_directory(FIXED_DIR)
    sched = scan_directory(SCHEDULED_DIR)
    for label, entities in sched.items():
        for key, var in entities.items():
            result.setdefault(label, {})[key] = var
    return result


def get_next_ids(force_refresh: bool = False) -> dict[str, int]:
    """获取下一个可用的各类型变量 ID"""
    state = get_batch_state()
    if state["latest_batch"] > 0 and not force_refresh:
        return state["next_ids"]

    fixed_used = scan_used_var_ids(FIXED_DIR)
    sched_used = scan_used_var_ids(SCHEDULED_DIR)
    used: dict[str, set[int]] = {}
    for d in (fixed_used, sched_used):
        for prefix, nums in d.items():
            used.setdefault(prefix, set()).update(nums)

    base = {"c": 984, "t": 17, "l": 34, "m": 30, "e": 21, "i": 215}
    result = {}
    for prefix, fallback in base.items():
        if prefix in used:
            result[prefix] = max(used[prefix]) + 1
        else:
            result[prefix] = fallback
    return result


# ============================================================
# 批次状态管理
# ============================================================

def get_batch_state() -> dict:
    """读取 index.json，不存在返回默认"""
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    return {
        "latest_batch": 0,
        "completed_batches": [],
        "total_entities_added": 0,
        "next_ids": {},
    }


def save_batch_state(state: dict):
    """写入 index.json"""
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ============================================================
# Cypher 生成函数
# ============================================================

def escape_value(val: str) -> str:
    """转义 Cypher 字符串中的双引号"""
    if not val:
        return ""
    return val.replace('"', '\\"')


def build_entity_statement(var: str, label: str, props: dict) -> str:
    """
    生成正确格式的 MERGE 语句。
    Character/Team → name_en + name 双字段
    """
    parts = []
    if label in ("Character", "Team"):
        name_en = props.get("name_en", "")
        parts.append(f'name_en: "{escape_value(name_en)}"')
        name_cn = props.get("name", "")
        if name_cn:
            parts.append(f'name: "{escape_value(name_cn)}"')
    elif label == "Movie":
        parts.append(f'title: "{escape_value(props.get("title", ""))}"')
    elif label == "Event":
        parts.append(f'event_name: "{escape_value(props.get("event_name", ""))}"')
    elif label == "Item":
        item_key = "item_name" if "item_name" in props else "name"
        parts.append(f'{item_key}: "{escape_value(props.get(item_key, ""))}"')
    else:
        parts.append(f'name: "{escape_value(props.get("name", ""))}"')

    for key, val in props.items():
        if key in ("name_en", "name", "title", "event_name", "item_name"):
            continue
        if val:
            parts.append(f'{key}: "{escape_value(str(val))}"')

    return f'MERGE ({var}:{label} {{{", ".join(parts)}}});'


def build_match_clause(var: str, label: str, props: dict) -> str:
    """生成 MATCH 子句片段，如 (c1:Character {name_en: "Iron Man"})"""
    if label in ("Character", "Team"):
        match_key = "name_en"
        match_val = props.get("name_en", "")
    elif label == "Movie":
        match_key = "title"
        match_val = props.get("title", "")
    elif label == "Event":
        match_key = "event_name"
        match_val = props.get("event_name", "")
    elif label == "Item":
        match_key = "item_name" if "item_name" in props else "name"
        match_val = props.get(match_key, "")
    else:
        match_key = "name"
        match_val = props.get("name", "")

    return f'({var}:{label} {{{match_key}: "{escape_value(match_val)}"}})'


def build_relationship_statement(
    src_var: str, src_label: str, src_props: dict,
    rel_type: str,
    tgt_var: str, tgt_label: str, tgt_props: dict,
    bidirectional: bool = False,
) -> list[str]:
    """生成 MATCH...MERGE 关系语句，返回语句列表"""
    src_match = build_match_clause(src_var, src_label, src_props)
    tgt_match = build_match_clause(tgt_var, tgt_label, tgt_props)
    rel_cn = REL_LABELS.get(rel_type, rel_type)

    stmts = [
        f"MATCH {src_match}, {tgt_match}",
        f"MERGE ({src_var})-[:{rel_cn}]->({tgt_var});",
    ]

    if bidirectional and rel_type in BIDIRECTIONAL_REL_TYPES:
        stmts.append(f"MATCH {tgt_match}, {src_match}")
        stmts.append(f"MERGE ({tgt_var})-[:{rel_cn}]->({src_var});")

    return stmts


# ============================================================
# 验证
# ============================================================

def validate_cypher(text: str) -> list[str]:
    """验证 Cypher 语句，返回错误列表。
    正确处理多行语句（MATCH + MERGE 跨行）。
    """
    errors = []
    lines = text.strip().split("\n")

    in_statement = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            in_statement = False
            continue

        # 检查全角引号
        if "“" in stripped or "”" in stripped or "＂" in stripped:
            errors.append(f"Line {i}: 含有全角引号")

        if stripped.startswith("MATCH"):
            in_statement = True
        elif stripped.startswith("MERGE"):
            in_statement = True
            # MERGE 行应加分号结尾（单句或末行）
            if not stripped.endswith(";"):
                errors.append(f"Line {i}: MERGE 语句缺少结尾分号: {stripped[:60]}")
        else:
            # 中间行（如属性换行）- 不做开头检查
            pass

    return errors


def validate_batch_dir(batch_dir: Path) -> list[str]:
    """验证批次目录下所有文件"""
    all_errors = []
    for fpath in sorted(batch_dir.glob("*.cypher")):
        text = fpath.read_text(encoding="utf-8")
        errors = validate_cypher(text)
        for err in errors:
            all_errors.append(f"{fpath.name}: {err}")
    return all_errors


# ============================================================
# 写入批次文件
# ============================================================

def write_batch_files(
    batch_num: int,
    entities: list[dict],
    relationships: list[list[str]],
) -> Path:
    """
    写入 scheduled_data/batch_NNN/ 下的各文件。
    entities: [{"var": "c984", "label": "Character", "props": {...}}, ...]
    relationships: [[stmt1, stmt2], ...]
    """
    batch_dir = SCHEDULED_DIR / f"batch_{batch_num:03d}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    # 按 label 分组实体
    by_label: dict[str, list[dict]] = {}
    for ent in entities:
        by_label.setdefault(ent["label"], []).append(ent)

    file_map = {
        "Character": ("characters.cypher", "角色"),
        "Team": ("teams.cypher", "团队"),
        "Location": ("locations.cypher", "地点"),
        "Movie": ("movies.cypher", "电影"),
        "Event": ("events.cypher", "事件"),
        "Item": ("items.cypher", "物品"),
    }

    for label, items in by_label.items():
        if label not in file_map:
            continue
        fname, cn_name = file_map[label]
        path = batch_dir / fname
        content = f"// {fname} — Batch {batch_num}\n// {len(items)} 个{cn_name}\n\n"
        for item in items:
            content += build_entity_statement(
                item["var"], item["label"], item["props"]
            ) + "\n"
        path.write_text(content, encoding="utf-8")

    # 关系文件
    if relationships:
        rel_path = batch_dir / "relationships.cypher"
        rel_lines = [f"// relationships.cypher — Batch {batch_num}"]
        rel_lines.append(f"// {len(relationships)} 条关系\n")
        for rel_stmts in relationships:
            rel_lines.append("\n".join(rel_stmts))
        rel_path.write_text("\n".join(rel_lines) + "\n", encoding="utf-8")

    return batch_dir


# ============================================================
# 报告生成
# ============================================================

def query_latest_batch_characters(batch_num: int) -> list[dict]:
    """读取最新批次的角色数据"""
    batch_dir = SCHEDULED_DIR / f"batch_{batch_num:03d}"
    char_file = batch_dir / "characters.cypher"
    if not char_file.exists():
        return []
    chars = []
    for line in char_file.read_text(encoding="utf-8").split("\n"):
        stripped = line.strip()
        if not stripped.startswith("MERGE (c"):
            continue
        parsed = parse_entity_statement(stripped)
        if parsed and parsed["label"] == "Character":
            chars.append(parsed["props"])
    return chars


def load_env() -> dict[str, str]:
    """从 .env 加载 Neo4j 配置"""
    env_path = ROOT / ".env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def generate_report() -> str:
    """
    从 Neo4j 查询完整数据，生成人类可读的 Markdown 报告。
    返回报告的文本内容，同时写到 REPORT.md。
    """
    env = load_env()
    uri = env.get("NEO4J_URI", "bolt://127.0.0.1:7687")
    user = env.get("NEO4J_USER", "neo4j")
    password = env.get("NEO4J_PASSWORD")
    database = env.get("NEO4J_DATABASE")

    if not password:
        return "# 报告生成失败\n\nNeo4j 未连接，请检查 .env 配置。"

    try:
        from neo4j import GraphDatabase
    except ImportError:
        return "# 报告生成失败\n\n需要安装 neo4j 驱动。"

    driver = GraphDatabase.driver(uri, auth=(user, password))
    state = get_batch_state()
    lines: list[str] = []
    now = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")

    def w(text: str = ""):
        lines.append(text)

    w("# 漫威宇宙数据收集总表")
    w(f"*最后更新: {now}*")
    w(f"*数据来源: fixed/（已审核）+ scheduled_data/（定时收集）*")
    w()

    # ------ 总体概览 ------
    w("---")
    w("## 📊 总体概览")
    w()

    with driver.session(database=database) as session:
        # 各类型节点数
        result = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC")
        node_counts = {r["label"]: r["cnt"] for r in result}
        total_nodes = sum(node_counts.values())

        # 关系总数
        rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

        # 各关系类型数
        result = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt ORDER BY cnt DESC")
        rel_types = {r["type"]: r["cnt"] for r in result}

        # 收集进度
        completed_count = len(state.get("completed_batches", []))

    w(f"- **节点总数**: {total_nodes}")
    w(f"- **关系总数**: {rel_count}")
    w()
    w("| 类型 | 数量 |")
    w("|------|-----:|")
    for label in ["Character", "Team", "Location", "Movie", "Event", "Item"]:
        cn_map = {"Character": "角色 👤", "Team": "团队 🏛️", "Location": "地点 📍",
                  "Movie": "电影 🎬", "Event": "事件 📖", "Item": "物品 ⚔️"}
        w(f"| {cn_map.get(label, label)} | {node_counts.get(label, 0)} |")

    w()
    w("| 关系类型 | 数量 |")
    w("|----------|-----:|")
    for rt, cnt in sorted(rel_types.items(), key=lambda x: -x[1]):
        w(f"| {rt} | {cnt} |")

    w()

    # ------ 各团队人员 ------
    w("---")
    w("## 🏛️ 各团队人员")
    w()

    with driver.session(database=database) as session:
        result = session.run(
            "MATCH (t:Team) RETURN t.name_en AS team, t.name AS team_cn ORDER BY t.name_en"
        )
        teams = [(r["team"], r["team_cn"]) for r in result]

    for team_en, team_cn in teams:
        with driver.session(database=database) as session:
            result = session.run(
                "MATCH (c:Character)-[:成员]->(t:Team {name_en: $team}) "
                "RETURN c.name_en, c.name ORDER BY c.name_en",
                team=team_en
            )
            members = [(r["c.name_en"], r["c.name"]) for r in result]

        if members:
            member_list = ", ".join(f"{cn}({en})" for en, cn in members)
            w(f"- **{team_cn}**（{team_en}）— {len(members)} 人: {member_list}")

    w()

    # ------ 敌人关系热点 ------
    w("---")
    w("## ⚔️ 敌对关系热度")
    w("最多敌人（树敌最多的前 10 名）:")
    w()

    with driver.session(database=database) as session:
        result = session.run(
            "MATCH (c:Character)-[:敌人]->() "
            "RETURN c.name_en, c.name, count(*) AS cnt "
            "ORDER BY cnt DESC LIMIT 10"
        )
        villains = [(r["c.name_en"], r["c.name"], r["cnt"]) for r in result]

    w("| 角色 | 敌人数量 |")
    w("|------|--------:|")
    for en, cn, cnt in villains:
        w(f"| {cn}({en}) | {cnt} |")

    w()
    w("最多盟友的前 10 名:")
    w()
    with driver.session(database=database) as session:
        result = session.run(
            "MATCH (c:Character)-[:盟友]->() "
            "RETURN c.name_en, c.name, count(*) AS cnt "
            "ORDER BY cnt DESC LIMIT 10"
        )
        allies = [(r["c.name_en"], r["c.name"], r["cnt"]) for r in result]
    w("| 角色 | 盟友数量 |")
    w("|------|--------:|")
    for en, cn, cnt in allies:
        w(f"| {cn}({en}) | {cnt} |")

    w()

    # ------ 最新批次 ------
    latest_batch = state.get("latest_batch", 0)
    if latest_batch > 0:
        w("---")
        w(f"## 🆕 最新批次（Batch {latest_batch}）")
        w()

        latest_chars = query_latest_batch_characters(latest_batch)
        if latest_chars:
            w(f"本批新增角色:")
            for c in latest_chars:
                w(f"- **{c.get('name', '?')}**（{c.get('name_en', '?')}）"
                  f"— {c.get('real_name', '?')}"
                  f" | {c.get('species', '?')}"
                  f" | {c.get('first_appearance', '?')}")
            w()

        # 最新关系摘要
        rel_file = SCHEDULED_DIR / f"batch_{latest_batch:03d}" / "relationships.cypher"
        if rel_file.exists():
            rel_count_in_file = 0
            for line in rel_file.read_text(encoding="utf-8").split("\n"):
                if line.strip().startswith("MERGE"):
                    rel_count_in_file += 1
            if rel_count_in_file > 0:
                # 找一些有趣的关系类型统计
                with driver.session(database=database) as session:
                    result = session.run(
                        "MATCH (c:Character)-[r]->(t) WHERE c.name_en IN $names "
                        "RETURN c.name_en AS src, type(r) AS rel, "
                        "CASE WHEN t:Character THEN t.name_en WHEN t:Team THEN t.name_en ELSE 'other' END AS tgt "
                        "LIMIT 20",
                        names=[c.get("name_en", "") for c in latest_chars if c.get("name_en")]
                    )
                    for r in result:
                        cn_map = {"成员": "加入", "敌人": "敌对", "盟友": "结盟",
                                  "亲属": "亲属", "来自": "来自", "使用": "使用", "使者": "侍奉", "出演": "出演"}
                        rel_word = cn_map.get(r["rel"], r["rel"])
                        w(f"- **{r['src']}** {rel_word} **{r['tgt']}**")

    # ------ 联网查询 ------
    w()
    w("---")
    w("## 🔍 样例查询")
    w()
    w("在 Neo4j Browser 中执行:")
    w()
    w("```cypher")
    w("// 找一个角色的完整关系网")
    w("MATCH (c:Character {name_en: 'Spider-Man'})-[r]-(connected)")
    w("RETURN c, type(r), connected")
    w()
    w("// 看看哪个团队人最多")
    w("MATCH (c:Character)-[:成员]->(t:Team)")
    w("RETURN t.name, count(c) AS members ORDER BY members DESC")
    w()
    w("// 查关联密度")
    w("MATCH (c:Character) WHERE size((c)-[]-()) > 10")
    w("RETURN c.name, size((c)-[]-()) AS connections ORDER BY connections DESC")
    w("```")
    w()

    driver.close()

    report = "\n".join(lines)

    # 写入文件
    report_path = ROOT / "REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    return report


# ============================================================
# 批次生成与导入（从 run_batch.py 迁移而来）
# ============================================================

def _find_props(existing: dict, name: str, label: str) -> dict:
    """
    返回最小的 props 字典，使 build_match_clause 能生成正确的 MATCH 子句。
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

    new_entities = []
    skipped_entities = 0
    entity_var_map: dict[str, str] = {}

    # --- 角色 ---
    for char_def in batch_def.get("characters", []):
        name_en = char_def.get("name_en", "")
        if not name_en:
            continue
        existing_var = existing.get("Character", {}).get(name_en)
        if existing_var:
            print(f"  ⏭️  角色已存在: {name_en} (var: {existing_var})")
            entity_var_map[name_en] = existing_var
            skipped_entities += 1
            continue
        var = f"c{id_counters['c']}"
        id_counters["c"] += 1
        entity_var_map[name_en] = var
        new_entities.append({"var": var, "label": "Character", "props": dict(char_def)})
        existing.setdefault("Character", {})[name_en] = var
        print(f"  ✅ 新角色: {var} → {name_en} ({char_def.get('name', '')})")

    # --- 团队 ---
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
        new_entities.append({"var": var, "label": "Team", "props": dict(team_def)})
        existing.setdefault("Team", {})[name_en] = var
        print(f"  ✅ 新团队: {var} → {name_en} ({team_def.get('name', '')})")

    # --- 地点 ---
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
        new_entities.append({"var": var, "label": "Location", "props": dict(loc_def)})
        existing.setdefault("Location", {})[name] = var
        print(f"  ✅ 新地点: {var} → {name}")

    # --- 电影 ---
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
        new_entities.append({"var": var, "label": "Movie", "props": dict(movie_def)})
        existing.setdefault("Movie", {})[title] = var
        print(f"  ✅ 新电影: {var} → {title}")

    # --- 事件 ---
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
        new_entities.append({"var": var, "label": "Event", "props": dict(event_def)})
        existing.setdefault("Event", {})[event_name] = var
        print(f"  ✅ 新事件: {var} → {event_name}")

    # --- 物品 ---
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
        new_entities.append({"var": var, "label": "Item", "props": dict(item_def)})
        existing.setdefault("Item", {})[item_key] = var
        print(f"  ✅ 新物品: {var} → {item_key}")

    # --- 关系 ---
    new_relationships = []
    skipped_rels = 0
    for rel_def in batch_def.get("relationships", []):
        src_name, src_label, rel_type, tgt_name, tgt_label = rel_def[:5]
        bidirectional = rel_def[5] if len(rel_def) > 5 else False
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

    if not new_entities and not new_relationships:
        print(f"\n📭 批次 {batch_index} 没有新增数据（所有实体已存在）")
        state.setdefault("completed_batches", []).append(str(batch_index))
        save_batch_state(state)
        return False

    batch_dir = write_batch_files(batch_index, new_entities, new_relationships)
    print(f"\n📁 写入: {batch_dir}")

    errors = validate_batch_dir(batch_dir)
    if errors:
        print("\n⚠️  验证发现以下问题:")
        for err in errors:
            print(f"  {err}")
    else:
        print("✅ 格式验证通过")

    state["latest_batch"] = batch_index
    state.setdefault("completed_batches", [])
    if str(batch_index) not in state["completed_batches"]:
        state["completed_batches"].append(str(batch_index))
    state["total_entities_added"] = state.get("total_entities_added", 0) + len(new_entities)
    state["next_ids"] = {p: id_counters[p] for p in ("c", "t", "l", "m", "e", "i")}
    save_batch_state(state)

    print(f"\n📊 批次统计:")
    print(f"  新增实体: {len(new_entities)}")
    print(f"  新增关系: {len(new_relationships)}")
    print(f"  跳过实体: {skipped_entities}")
    print(f"  跳过关系: {skipped_rels}")
    print(f"  累计实体: {state['total_entities_added']}")

    if import_after:
        import_batch_to_neo4j(batch_index, batch_dir)

    print("\n📝 更新报告...")
    try:
        generate_report()
        print("✅ REPORT.md 已更新")
    except Exception as e:
        print(f"⚠️ 报告生成失败: {e}")

    return True


def import_batch_to_neo4j(batch_index: int, batch_dir: Path = None):
    """将指定批次导入 Neo4j（读取 .env 连接配置）"""
    if batch_dir is None:
        batch_dir = SCHEDULED_DIR / f"batch_{batch_index:03d}"

    if not batch_dir.exists():
        print(f"❌ 批次目录不存在: {batch_dir}")
        return False

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

    cypher_files = sorted(batch_dir.glob("*.cypher"))
    total_stmts = 0
    success = 0
    failed = 0

    for fpath in cypher_files:
        content = fpath.read_text(encoding="utf-8")
        raw_stmts = content.split(";")
        stmts = []
        for chunk in raw_stmts:
            chunk = chunk.strip()
            if not chunk:
                continue
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


def print_status():
    """打印收集进度"""
    state = get_batch_state()
    fixed = scan_directory(FIXED_DIR)
    scheduled = scan_directory(SCHEDULED_DIR)

    print("\n" + "=" * 60)
    print("  漫威数据收集进度")
    print("=" * 60)

    total_fixed = sum(len(v) for v in fixed.values())
    total_scheduled = sum(len(v) for v in scheduled.values())

    print(f"\n📁 fixed/（已审核）: {total_fixed} 个实体")
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
