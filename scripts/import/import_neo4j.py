#!/usr/bin/env python3
"""Import local graph artifacts into Neo4j."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ENV_FILE = ROOT / ".env"
DEFAULT_NODES = DATA_DIR / "nodes.csv"
DEFAULT_EDGES = DATA_DIR / "edges.csv"
DEFAULT_TRACE = DATA_DIR / "neo4j_import_trace.json"

SAFE_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [dict(row) for row in csv.DictReader(f)]


def read_properties(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        return {}
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def safe_identifier(value: str, kind: str) -> str:
    if not SAFE_IDENTIFIER.match(value):
        raise ValueError(f"Unsafe {kind}: {value}")
    return value


def chunks(rows: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [rows[index : index + size] for index in range(0, len(rows), size)]


def normalize_nodes(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        label = safe_identifier(row["label"], "label")
        props = read_properties(row.get("properties", ""))
        props.update(
            {
                "id": row["id"],
                "key": row.get("key", ""),
                "name": row.get("name", ""),
                "label": label,
            }
        )
        output.append({"id": row["id"], "label": label, "props": props})
    return output


def normalize_edges(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        rel_type = safe_identifier(row["type"], "relationship type")
        props = read_properties(row.get("properties", ""))
        props.update({"id": row["id"], "type": rel_type})
        output.append(
            {
                "id": row["id"],
                "source": row["source"],
                "target": row["target"],
                "type": rel_type,
                "props": props,
            }
        )
    return output


def create_constraints(driver, labels: list[str], database: str | None) -> None:
    with driver.session(database=database) as session:
        for label in sorted(set(labels)):
            safe_label = safe_identifier(label, "label")
            constraint_name = f"team_mgt_{safe_label.lower()}_id_unique"
            query = (
                f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
                f"FOR (n:{safe_label}) REQUIRE n.id IS UNIQUE"
            )
            session.run(query).consume()


def import_nodes(driver, nodes: list[dict[str, Any]], batch_size: int, database: str | None) -> int:
    imported = 0
    labels = sorted({node["label"] for node in nodes})
    with driver.session(database=database) as session:
        for label in labels:
            safe_label = safe_identifier(label, "label")
            label_nodes = [node for node in nodes if node["label"] == label]
            query = (
                f"UNWIND $rows AS row "
                f"MERGE (n:{safe_label} {{id: row.id}}) "
                f"SET n += row.props"
            )
            for batch in chunks(label_nodes, batch_size):
                session.run(query, rows=batch).consume()
                imported += len(batch)
    return imported


def import_edges(driver, edges: list[dict[str, Any]], batch_size: int, database: str | None) -> int:
    imported = 0
    rel_types = sorted({edge["type"] for edge in edges})
    with driver.session(database=database) as session:
        for rel_type in rel_types:
            safe_rel_type = safe_identifier(rel_type, "relationship type")
            rel_edges = [edge for edge in edges if edge["type"] == rel_type]
            query = (
                "UNWIND $rows AS row "
                "MATCH (source {id: row.source}) "
                "MATCH (target {id: row.target}) "
                f"MERGE (source)-[rel:{safe_rel_type} {{id: row.id}}]->(target) "
                "SET rel += row.props"
            )
            for batch in chunks(rel_edges, batch_size):
                session.run(query, rows=batch).consume()
                imported += len(batch)
    return imported


def verify_import(driver, database: str | None) -> dict[str, Any]:
    query = """
    MATCH (n)
    WITH count(n) AS node_count
    MATCH ()-[r]->()
    RETURN node_count, count(r) AS relationship_count
    """
    group_query = """
    MATCH (g:Group)<-[:MEMBER_OF]-(p:Person)-[:LOGGED]->(w:Worklog)
    RETURN g.name AS group, round(sum(toFloat(w.hours)), 4) AS hours, count(DISTINCT p) AS people
    ORDER BY hours DESC
    """
    total_query = """
    MATCH (:Person)-[:LOGGED]->(w:Worklog)
    RETURN round(sum(toFloat(w.hours)), 4) AS total_hours, count(w) AS worklog_count
    """
    labels_query = """
    MATCH (n)
    RETURN labels(n)[0] AS label, count(n) AS count
    ORDER BY label
    """
    rels_query = """
    MATCH ()-[r]->()
    RETURN type(r) AS type, count(r) AS count
    ORDER BY type
    """
    with driver.session(database=database) as session:
        counts = session.run(query).single().data()
        total = session.run(total_query).single().data()
        group_rows = [record.data() for record in session.run(group_query)]
        label_rows = [record.data() for record in session.run(labels_query)]
        rel_rows = [record.data() for record in session.run(rels_query)]
    return {
        "counts": counts,
        "total_worklog_hours": total,
        "hours_by_group": group_rows,
        "labels": label_rows,
        "relationship_types": rel_rows,
    }


def main() -> None:
    load_env_file()
    parser = argparse.ArgumentParser(description="Import local ontology graph into Neo4j.")
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD"))
    parser.add_argument("--database", default=os.getenv("NEO4J_DATABASE"))
    parser.add_argument("--nodes", type=Path, default=DEFAULT_NODES)
    parser.add_argument("--edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--skip-constraints", action="store_true")
    args = parser.parse_args()

    if not args.password:
        raise SystemExit("Neo4j password is required via --password or NEO4J_PASSWORD.")

    node_rows = normalize_nodes(read_csv(args.nodes))
    edge_rows = normalize_edges(read_csv(args.edges))
    labels = sorted({node["label"] for node in node_rows})

    started_at = datetime.now()
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    try:
        driver.verify_connectivity()
        if not args.skip_constraints:
            create_constraints(driver, labels, args.database)
        imported_nodes = import_nodes(driver, node_rows, args.batch_size, args.database)
        imported_edges = import_edges(driver, edge_rows, args.batch_size, args.database)
        verification = verify_import(driver, args.database)
    finally:
        driver.close()

    trace = {
        "started_at": started_at.isoformat(timespec="seconds"),
        "ended_at": datetime.now().isoformat(timespec="seconds"),
        "uri": args.uri,
        "database": args.database or "(default)",
        "nodes_file": str(args.nodes),
        "edges_file": str(args.edges),
        "node_rows": len(node_rows),
        "edge_rows": len(edge_rows),
        "imported_nodes": imported_nodes,
        "imported_edges": imported_edges,
        "labels": labels,
        "relationship_types": sorted({edge["type"] for edge in edge_rows}),
        "verification": verification,
    }
    write_json(args.trace, trace)
    print(json.dumps(trace, ensure_ascii=False, indent=2))
    print(f"trace={args.trace}")


if __name__ == "__main__":
    main()
