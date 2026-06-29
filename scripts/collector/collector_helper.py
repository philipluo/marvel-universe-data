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
from pathlib import Path
from typing import Any

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
