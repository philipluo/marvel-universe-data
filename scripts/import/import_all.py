#!/usr/bin/env python3
"""
One-shot import of ALL data from ori/import_data_clean_fixed.cypher into Neo4j.

Key tasks:
1. Deduplicate (the source file has Chinese + 8x English duplicate copies)
2. Convert Team: name -> name_en + Chinese name field
3. Parse entity properties so relationships can use MATCH+MERGE correctly
4. Generate clean batch files under fixed/ matching the progress.md scheme
"""

import os
import re
import sys
from pathlib import Path
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
SOURCE_FILE = ROOT / "ori" / "import_data_clean_fixed.cypher"
FIXED_DIR = ROOT / "fixed"

# ============================================================
# Team name -> name_en conversion mapping
# ============================================================
TEAM_ZH_NAMES = {
    "Avengers": "复仇者联盟",
    "S.H.I.E.L.D.": "神盾局",
    "Stark Industries": "斯塔克工业",
    "Fantastic Four": "神奇四侠",
    "X-Men": "X战警",
    "Brotherhood of Mutants": "变种人兄弟会",
    "Guardians of the Galaxy": "银河护卫队",
    "Defenders": "捍卫者联盟",
    "Heroes for Hire": "雇佣英雄",
    "Young Avengers": "少年复仇者",
    "Secret Avengers": "秘密复仇者",
    "West Coast Avengers": "西海岸复仇者",
    "A-Force": "A-Force",
    "New Avengers": "新复仇者",
    "Savage Avengers": "野蛮复仇者",
}


REL_TYPE_ZH = {
    "MEMBER_OF": "成员",
    "ENEMY_OF": "敌人",
    "ALLY_OF": "盟友",
    "FROM": "来自",
    "USES": "使用",
    "RELATIVE_OF": "亲属",
    "HERALD_OF": "使者",
}

# Bidirectional relationship types: if A-[r]->B exists, also create B-[r]->A
BIDIRECTIONAL_REL_TYPES = {"ENEMY_OF", "ALLY_OF"}


def translate_rel_type(stmt: str) -> str:
    """Replace English relationship type names with Chinese in a Cypher statement."""
    def _replace(match):
        eng_type = match.group(1)
        if eng_type in REL_TYPE_ZH:
            return f"[:{REL_TYPE_ZH[eng_type]}"
        return match.group(0)

    return re.sub(r"\[:(\w+)", _replace, stmt)


def load_env():
    if not ENV_FILE.exists():
        print(f"ERROR: .env not found at {ENV_FILE}")
        sys.exit(1)
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def split_statements(text: str):
    """Split Cypher text into individual statements."""
    text = re.sub(r"//.*", "", text)
    text = text.strip()
    for stmt in text.split(";"):
        stmt = stmt.strip()
        if stmt:
            yield stmt + ";"


def extract_var_name(stmt: str) -> str | None:
    m = re.match(r"MERGE\s+\((\w+):", stmt)
    return m.group(1) if m else None


def extract_label(stmt: str) -> str | None:
    m = re.match(r"MERGE\s+\(\w+:(\w+)", stmt)
    return m.group(1) if m else None


def has_chinese(s: str) -> bool:
    return bool(re.search(r"[一-鿿]", s))


def is_relationship_direct(stmt: str) -> bool:
    return bool(re.match(r"MERGE\s+\(\w+\)\s*-\[", stmt))


def fix_team_name(stmt: str) -> str:
    """Convert Team name field to name_en + name pattern, keeping existing fields."""
    m = re.match(r"(MERGE\s+\(\w+:Team\s*\{)(.*?)(\}\);?)$", stmt, re.DOTALL)
    if not m:
        return stmt

    prefix = m.group(1)
    props_str = m.group(2)
    suffix = m.group(3)

    # Parse properties - handle quoted values properly
    props = {}
    # Simple state machine for parsing props
    i = 0
    while i < len(props_str):
        # Skip whitespace
        while i < len(props_str) and props_str[i] in ' \t\n\r,':
            i += 1
        if i >= len(props_str):
            break
        # key: value
        key_match = re.match(r'(\w+):\s*', props_str[i:])
        if key_match:
            key = key_match.group(1)
            i += key_match.end()
            # Value - could be quoted string or unquoted
            if i < len(props_str) and props_str[i] == '"':
                # Quoted string - find closing quote
                i += 1  # skip opening "
                val = ""
                while i < len(props_str):
                    if props_str[i] == '\\' and i + 1 < len(props_str):
                        val += props_str[i+1]
                        i += 2
                    elif props_str[i] == '"':
                        i += 1
                        break
                    else:
                        val += props_str[i]
                        i += 1
                props[key] = val
            else:
                # Unquoted value - read until comma or end
                val_match = re.match(r'([^,}\n]+)', props_str[i:])
                if val_match:
                    val = val_match.group(1).strip()
                    i += val_match.end()
                    props[key] = val

    if "name" not in props:
        return stmt

    old_name = props["name"]
    zh_name = TEAM_ZH_NAMES.get(old_name, "")

    # Build new properties
    new_props = {}
    for k, v in props.items():
        if k == "name":
            new_props["name_en"] = v
            if zh_name:
                new_props["name"] = zh_name
        else:
            new_props[k] = v

    if not zh_name and "name" not in new_props:
        new_props["name"] = old_name

    new_props_str = ", ".join(f'{k}: "{v}"' for k, v in new_props.items())
    return f"{prefix}{new_props_str}{suffix}"


# ============================================================
# Property extraction for MATCH building
# ============================================================

def parse_entity_props(stmt: str) -> dict[str, str]:
    """Extract properties from a MERGE entity statement."""
    m = re.match(r"MERGE\s+\(\w+:\w+\s*\{(.*)\}\)", stmt, re.DOTALL)
    if not m:
        return {}
    props_str = m.group(1)
    props = {}
    i = 0
    while i < len(props_str):
        while i < len(props_str) and props_str[i] in ' \t\n\r,':
            i += 1
        if i >= len(props_str):
            break
        key_match = re.match(r'(\w+):\s*', props_str[i:])
        if key_match:
            key = key_match.group(1)
            i += key_match.end()
            if i < len(props_str) and props_str[i] == '"':
                i += 1
                val = ""
                while i < len(props_str):
                    if props_str[i] == '\\' and i + 1 < len(props_str):
                        val += props_str[i+1]
                        i += 2
                    elif props_str[i] == '"':
                        i += 1
                        break
                    else:
                        val += props_str[i]
                        i += 1
                props[key] = val
            else:
                val_match = re.match(r'([^,}\n]+)', props_str[i:])
                if val_match:
                    val = val_match.group(1).strip()
                    i += val_match.end()
                    props[key] = val
    return props


def build_match_for_var(var: str, label: str, props: dict[str, str]) -> str:
    """Build MATCH clause like (c100:Character {name_en: 'Spider-Man'})."""
    # Pick the best unique identifying property
    if label == "Character":
        match_key = "name_en"
    elif label == "Team":
        match_key = "name_en"
    elif label == "Item":
        # Items use either name or item_name
        match_key = "name" if "name" in props else "item_name"
    elif label == "Location":
        match_key = "name"
    elif label == "Movie":
        match_key = "title"
    elif label == "Event":
        match_key = "event_name"
    else:
        # Fallback: use any available string property
        for key in ("name_en", "name", "title", "event_name", "item_name"):
            if key in props and props[key]:
                match_key = key
                break
        else:
            return f"({var}:{label})"

    if match_key in props and props[match_key]:
        val = props[match_key].replace("'", "\\'")
        return f"({var}:{label} {{{match_key}: '{val}'}})"
    else:
        return f"({var}:{label})"


# ============================================================
# Main processing
# ============================================================

def process_source():
    """Read source, deduplicate, build var props table, return structured data."""
    text = SOURCE_FILE.read_text(encoding="utf-8")
    raw_stmts = list(split_statements(text))
    print(f"Raw statements from source: {len(raw_stmts)}")

    seen_entity_vars: set[str] = set()
    entity_stmts: list[str] = []
    var_labels: dict[str, str] = {}
    var_props: dict[str, dict[str, str]] = {}
    raw_rel_stmts: list[str] = []

    for stmt in raw_stmts:
        if is_relationship_direct(stmt):
            raw_rel_stmts.append(stmt)
        else:
            var = extract_var_name(stmt)
            label = extract_label(stmt)
            if var:
                var_labels[var] = label
                props = parse_entity_props(stmt)
                var_props[var] = props

                if var in seen_entity_vars:
                    # Keep Chinese version
                    has_zh = has_chinese(stmt)
                    old_has_zh = False
                    for i, old in enumerate(entity_stmts):
                        if extract_var_name(old) == var:
                            old_has_zh = has_chinese(old)
                            if has_zh and not old_has_zh:
                                entity_stmts[i] = stmt
                            break
                    continue

                seen_entity_vars.add(var)
                entity_stmts.append(stmt)

    # Fix Team names
    fixed_entities = []
    for stmt in entity_stmts:
        var = extract_var_name(stmt)
        if var and var_labels.get(var) == "Team":
            stmt = fix_team_name(stmt)
            var_props[var] = parse_entity_props(stmt)

        # Fix Mandarin's (c923) real_name: "Kang the Conqueror" is wrong, it should be "Khan"
        if var == "c923" and "Kang the Conqueror" in stmt:
            stmt = stmt.replace('real_name: "Kang the Conqueror"', 'real_name: "Khan"')
            print(f"  ✎ Fixed Mandarin real_name: Kang the Conqueror -> Khan")
            var_props[var] = parse_entity_props(stmt)

        fixed_entities.append(stmt)

    print(f"Deduplicated entity statements: {len(fixed_entities)}")
    print(f"Raw relationship statements: {len(raw_rel_stmts)}")

    # Convert relationships
    converted_rels = convert_relationships(raw_rel_stmts, var_labels, var_props)

    # Apply data corrections for known missing relationships
    print("\n--- Data Corrections ---")
    corrections = get_data_corrections(var_labels, var_props)
    converted_rels.extend(corrections)

    return fixed_entities, converted_rels, var_labels, var_props


def convert_relationships(
    rel_stmts: list[str],
    var_labels: dict[str, str],
    var_props: dict[str, dict[str, str]],
) -> list[str]:
    """Convert direct MERGE relationships to MATCH+MERGE with specific properties."""
    converted = []
    seen_rels: set[str] = set()
    skipped_label = 0
    skipped_dup = 0

    for stmt in rel_stmts:
        clean = re.sub(r"\s+", " ", stmt).strip()
        if clean in seen_rels:
            skipped_dup += 1
            continue
        seen_rels.add(clean)

        # Extract all variables used in this relationship
        vars_used = re.findall(r"\((\w+)\)", stmt)
        # Also check for label-qualified vars
        qualified = re.findall(r"\((\w+):\w+", stmt)
        # Only use non-qualified variables as source/target
        # Actually, any variable used is a candidate
        if qualified:
            continue  # Skip already-processed statements

        # Build MATCH clauses for all variables
        match_parts = []
        can_build = True
        for v in vars_used:
            if v in var_labels and v in var_props:
                match_part = build_match_for_var(v, var_labels[v], var_props[v])
                match_parts.append(match_part)
            elif v in var_labels:
                # Have label but no props - just use label match
                match_parts.append(f"({v}:{var_labels[v]})")
            else:
                # No label info available - skip
                can_build = False
                break

        if not can_build or not match_parts:
            skipped_label += 1
            continue

        match_clause = "MATCH " + ", ".join(match_parts)
        stmt_clean = stmt.rstrip(";")
        result = f"{match_clause}\n{stmt_clean};"
        result = translate_rel_type(result)
        converted.append(result)

        # For bidirectional types (ENEMY_OF, ALLY_OF), also create the reverse relationship
        rel_type_match = re.search(r"-\[:(\w+)\]->", stmt)
        if rel_type_match and rel_type_match.group(1) in BIDIRECTIONAL_REL_TYPES:
            # Extract source and target variables from the MERGE pattern
            # Original: MERGE (source)-[:REL]->(target)
            merge_match = re.match(r"\s*MERGE\s+\((\w+)\)-\s*\[:(\w+)\]\s*->\s*\((\w+)\)", stmt)
            if merge_match:
                src_var, rel_type, tgt_var = merge_match.group(1), merge_match.group(2), merge_match.group(3)
                # Build reverse statement: MERGE (tgt)-[:REL]->(src)
                rev_stmt = f"MERGE ({tgt_var})-[:{rel_type}]->({src_var});"
                rev_result = f"{match_clause}\n{rev_stmt}"
                rev_result = translate_rel_type(rev_result)
                converted.append(rev_result)

    print(f"Converted relationships: {len(converted)}, "
          f"skipped (dup): {skipped_dup}, skipped (no label): {skipped_label}")
    return converted


def get_data_corrections(var_labels: dict[str, str], var_props: dict[str, dict[str, str]]) -> list[str]:
    """
    Generate additional relationship statements to fix known data gaps in the source.
    Each correction is a MATCH+MERGE pair using name_en for precise matching.
    """
    corrections = []

    def add_rel(src_var: str, rel_zh: str, tgt_var: str, bidirectional: bool = True):
        src_label = var_labels.get(src_var, "Character")
        tgt_label = var_labels.get(tgt_var, "Character")
        src_props = var_props.get(src_var, {})
        tgt_props = var_props.get(tgt_var, {})

        src_match = build_match_for_var(src_var, src_label, src_props)
        tgt_match = build_match_for_var(tgt_var, tgt_label, tgt_props)

        stmt = (
            f"MATCH {src_match}, {tgt_match}\n"
            f"MERGE ({src_var})-[:{rel_zh}]->({tgt_var});"
        )
        corrections.append(stmt)
        # For bidirectional types (敌人/盟友), create reverse direction too
        if bidirectional and rel_zh in ("敌人", "盟友"):
            rev_stmt = (
                f"MATCH {tgt_match}, {src_match}\n"
                f"MERGE ({tgt_var})-[:{rel_zh}]->({src_var});"
            )
            corrections.append(rev_stmt)

    # --- Fix missing enemy relationships ---
    # Mandarin (c923) should be enemy of Iron Man (c1)
    corrections.append("// Correction: Mandarin -> Iron Man (Mandarin is Iron Man's arch-nemesis)")
    add_rel("c923", "敌人", "c1")

    # Ultron (c305) should be enemy of Iron Man (c1)
    corrections.append("// Correction: Ultron -> Iron Man")
    add_rel("c305", "敌人", "c1")

    # Doctor Doom (c302) should be enemy of Iron Man (c1)
    corrections.append("// Correction: Doctor Doom -> Iron Man")
    add_rel("c302", "敌人", "c1")

    # Note: Mandarin's real_name is "Kang the Conqueror" in source data, which is incorrect
    # (Mandarin's real name is not Kang). This is a source data quality issue.

    print(f"Data corrections added: {len(corrections)}")
    for c in corrections:
        if not c.startswith("//"):
            print(f"  {c[:80]}...")
    return corrections


def generate_batch_files(entities: list[str], relationships: list[str], var_labels: dict[str, str], var_props: dict[str, dict[str, str]]):
    """Generate organized batch files."""
    FIXED_DIR.mkdir(parents=True, exist_ok=True)

    def var_in(vars_set):
        return lambda s: extract_var_name(s) in vars_set if extract_var_name(s) else False

    def rel_uses_vars(vars_set):
        """Check if relationship uses any of the given variables."""
        def check(s):
            # Find all variables: simple (c100) in MERGE part and qualified (c100:Character) in MATCH part
            simple_vars = re.findall(r"\((\w+)\)", s)           # (c100)
            qualified_vars = re.findall(r"\((\w+):\w+", s)      # (c100:Character)
            all_vars = set(simple_vars) | set(qualified_vars)
            return any(v in vars_set for v in all_vars)
        return check

    # Batch definitions
    batches = {
        "p2": {f"c{100+i}" for i in range(8)},
        "p3": {f"c{200+i}" for i in range(9)},
        "p4": {f"c{300+i}" for i in range(7)},
        "p5": {f"c{400+i}" for i in range(7)},
        "p6": {f"c{500+i}" for i in range(4)},
        "p7": {f"c{600+i}" for i in range(11)},
        "p8": {f"c{700+i}" for i in range(10)} | {"c705", "c707", "c708", "c709"},
        "p9": {f"c{800+i}" for i in range(7)},
        "p10": {f"c{900+i}" for i in range(4)},
        "p11": {f"c{910+i}" for i in range(6)},
        "p12": {f"c{921+i}" for i in range(3)},
        "p13": {f"c{930+i}" for i in range(5)},
        "p14": {f"c{941+i}" for i in range(2)},
        "p15": {f"c{950+i}" for i in range(6)},
        "p16": {f"c{960+i}" for i in range(4)},
        "p17": {f"c{970+i}" for i in range(4)},
        "p18": {f"c{980+i}" for i in range(4)},
    }

    written = []
    for bname, bvars in batches.items():
        char_stmts = [s for s in entities if extract_var_name(s) in bvars and extract_label(s) == "Character"]
        team_stmts = [s for s in entities if extract_var_name(s) in bvars and extract_label(s) == "Team"]
        rel_stmts = [s for s in relationships if rel_uses_vars(bvars)(s)]

        if char_stmts:
            path = FIXED_DIR / f"{bname}_characters.cypher"
            path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in char_stmts), encoding="utf-8")
            written.append(path)

        if team_stmts:
            path = FIXED_DIR / f"{bname}_teams.cypher"
            path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in team_stmts), encoding="utf-8")
            written.append(path)

        if rel_stmts:
            path = FIXED_DIR / f"{bname}_relationships.cypher"
            path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in rel_stmts), encoding="utf-8")
            written.append(path)

    # Extra entities
    team_prefixes = {f"t{i}" for i in range(1, 17)}
    extra_teams = [s for s in entities if extract_label(s) == "Team" if extract_var_name(s) not in {"t1", "t2", "t3"}]
    if extra_teams:
        path = FIXED_DIR / "entities_teams_extra.cypher"
        path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in extra_teams), encoding="utf-8")
        written.append(path)

    extra_locs = [s for s in entities if extract_label(s) == "Location" if extract_var_name(s) not in {"l1", "l2", "l3"}]
    if extra_locs:
        path = FIXED_DIR / "entities_locations_extra.cypher"
        path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in extra_locs), encoding="utf-8")
        written.append(path)

    movies = [s for s in entities if extract_label(s) == "Movie"]
    if movies:
        path = FIXED_DIR / "entities_movies.cypher"
        path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in movies), encoding="utf-8")
        written.append(path)

    events = [s for s in entities if extract_label(s) == "Event"]
    if events:
        path = FIXED_DIR / "entities_events.cypher"
        path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in events), encoding="utf-8")
        written.append(path)

    extra_items = [s for s in entities if extract_label(s) == "Item" if extract_var_name(s) not in {f"i{i}" for i in range(1, 8)}]
    if extra_items:
        path = FIXED_DIR / "entities_items_extra.cypher"
        path.write_text("// " + path.name + "\n\n" + "\n".join(s + "\n" for s in extra_items), encoding="utf-8")
        written.append(path)

    print(f"\nGenerated {len(written)} batch files:")
    for p in written:
        print(f"  {p.name}")

    # Write data corrections as a separate file
    correction_stmts = [s for s in relationships if s.startswith("// Correction:")]
    corr_rels = []
    for i, s in enumerate(relationships):
        if s.startswith("// Correction:"):
            if i + 1 < len(relationships):
                corr_rels.append(relationships[i + 1])
    if correction_stmts:
        lines = []
        lines.append("// data_corrections.cypher")
        lines.append("// Manually added relationships to fix known source data gaps\n")
        for comment, stmt in zip(correction_stmts, corr_rels):
            lines.append(comment)
            lines.append(stmt)
        path = FIXED_DIR / "data_corrections.cypher"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written.append(path)
        print(f"  {path.name}")


def import_to_neo4j(all_entities: list[str], all_relationships: list[str]):
    """Import all entities and relationships into Neo4j."""
    load_env()

    uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")

    if not password:
        print("ERROR: NEO4J_PASSWORD not set in .env")
        sys.exit(1)

    print(f"\nConnecting to {uri}  db={database or '(default)'}  user={user}")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        driver.verify_connectivity()
        print("✓ Connected to Neo4j\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

    # Clear existing data
    with driver.session(database=database) as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    print("✓ Cleared existing data")

    # Import entities in batches by label
    from collections import defaultdict
    by_label: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for stmt in all_entities:
        label = extract_label(stmt) or "Unknown"
        var = extract_var_name(stmt) or "x"
        by_label[label].append((var, stmt))

    entity_success = 0
    entity_fail = 0
    with driver.session(database=database) as session:
        for label, items in sorted(by_label.items()):
            print(f"  {label}: {len(items)} nodes")
            for var, stmt in items:
                try:
                    session.run(stmt).consume()
                    entity_success += 1
                except Exception as e:
                    print(f"    ✗ {var} failed: {e}")
                    entity_fail += 1

    print(f"  Entities imported: {entity_success} OK, {entity_fail} failed")

    # Import relationships (skip comment lines)
    actual_rels = [s for s in all_relationships if not s.strip().startswith("//")]
    print(f"\n  Relationships: {len(actual_rels)} statements (from {len(all_relationships)} total lines)")
    rel_success = 0
    rel_fail = 0
    with driver.session(database=database) as session:
        for i, stmt in enumerate(actual_rels, 1):
            try:
                session.run(stmt).consume()
                rel_success += 1
            except Exception as e:
                print(f"    ✗ Statement {i} failed: {e}")
                rel_fail += 1

    print(f"  Relationships imported: {rel_success} OK, {rel_fail} failed")

    # Verify
    print("\n--- Verification ---")
    with driver.session(database=database) as session:
        result = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label")
        rows = [r.data() for r in result]
        total_nodes = sum(r["count"] for r in rows)
        print(f"\nNodes by label (total: {total_nodes}):")
        for r in rows:
            print(f"  {r['label']}: {r['count']}")

        result = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type")
        rows = [r.data() for r in result]
        total_rels = sum(r["count"] for r in rows)
        print(f"\nRelationships by type (total: {total_rels}):")
        for r in rows:
            print(f"  {r['type']}: {r['count']}")

    driver.close()
    print(f"\n✓ Done! {entity_success} entities, {rel_success} relationships.")


def main():
    print("=" * 60)
    print("  Marvel Graph Import - All Batches")
    print("=" * 60)

    print("\n[1/3] Processing source file...")
    entities, relationships, var_labels, var_props = process_source()

    print("\n[2/3] Generating batch files...")
    generate_batch_files(entities, relationships, var_labels, var_props)

    print("\n[3/3] Importing into Neo4j...")
    import_to_neo4j(entities, relationships)

    print("\n✓ All complete!")


if __name__ == "__main__":
    main()
