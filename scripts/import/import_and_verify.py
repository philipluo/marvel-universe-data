#!/usr/bin/env python3
"""Import the fixed/ Cypher files into Neo4j and verify the result."""

import os
import sys
import re
from pathlib import Path
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
FIXED_DIR = ROOT / "fixed"
FILES = [
    "entities_characters_p1.cypher",
    "entities_teams_p1.cypher",
    "entities_items_p1.cypher",
    "entities_locations_p1.cypher",
    "relationships_p1.cypher",
]


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
    """Split Cypher text into individual statements (split on ;)."""
    text = re.sub(r"//.*", "", text)  # strip comments
    text = text.strip()
    for stmt in text.split(";"):
        stmt = stmt.strip()
        if stmt:
            yield stmt + ";"


def main():
    load_env()

    uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")

    if not password:
        print("ERROR: NEO4J_PASSWORD not set in .env")
        sys.exit(1)

    print(f"Connecting to {uri}  db={database or '(default)'}  user={user}")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        driver.verify_connectivity()
        print("✓ Connected to Neo4j\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

    # Clear existing data first
    with driver.session(database=database) as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    print("✓ Cleared existing data\n")

    # Execute each file
    for filename in FILES:
        path = FIXED_DIR / filename
        if not path.exists():
            print(f"  SKIP {filename} (not found)")
            continue

        content = path.read_text(encoding="utf-8")
        statements = list(split_statements(content))
        print(f"  {filename}: {len(statements)} statements")

        with driver.session(database=database) as session:
            for i, stmt in enumerate(statements, 1):
                try:
                    session.run(stmt).consume()
                except Exception as e:
                    print(f"    ✗ Statement {i} failed: {e}")
                    print(f"      SQL: {stmt[:120]}...")
                    sys.exit(1)
        print(f"    ✓ All executed")

    # Verify
    print("\n--- Verification ---")
    with driver.session(database=database) as session:
        # 1. Count nodes by label
        result = session.run(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label"
        )
        rows = [r.data() for r in result]
        print("\nNodes by label:")
        for r in rows:
            print(f"  {r['label']}: {r['count']}")

        # 2. Count relationships by type
        result = session.run(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type"
        )
        rows = [r.data() for r in result]
        print("\nRelationships by type:")
        for r in rows:
            print(f"  {r['type']}: {r['count']}")

        # 3. THE KEY QUERY: Character -> Team
        result = session.run(
            "MATCH (c:Character)-[:MEMBER_OF]->(t:Team) "
            "RETURN c.name AS character, t.name_en AS team, t.name AS team_zh "
            "ORDER BY c.name"
        )
        rows = [r.data() for r in result]
        print(f"\nCharacter -> Team (MEMBER_OF): {len(rows)} rows")
        for r in rows:
            print(f"  {r['character']} -> {r['team']} ({r['team_zh']})")

    driver.close()
    print(f"\n✓ Done. Run `cypher-shell` or Browser to explore.")


if __name__ == "__main__":
    main()
