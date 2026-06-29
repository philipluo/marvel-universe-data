#!/usr/bin/env python3
"""
Import fixed/relationships_movie_appearances.cypher into Neo4j.
Safe to run multiple times — all statements use MATCH+MERGE (idempotent).
"""
import os, re, sys
from pathlib import Path
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[2]
ENV = ROOT / ".env"
FILE = ROOT / "fixed" / "relationships_movie_appearances.cypher"

def load_env():
    env = {}
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip("\"").strip("'")
    return env

def main():
    env = load_env()
    uri = env["NEO4J_URI"]
    user = env["NEO4J_USER"]
    password = env["NEO4J_PASSWORD"]
    db = env.get("NEO4J_DATABASE")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print(f"Connected to {uri}")

    content = FILE.read_text()
    text = re.sub(r"//.*", "", content)
    stmts = [s.strip() + ";" for s in text.split(";") if s.strip()]
    print(f"Found {len(stmts)} statements")

    ok = fail = 0
    with driver.session(database=db) as session:
        for stmt in stmts:
            try:
                session.run(stmt).consume()
                ok += 1
            except Exception as e:
                fail += 1
                if fail <= 3:
                    print(f"  FAIL: {str(e)[:80]}")

    driver.close()
    print(f"\nResult: {ok} succeeded, {fail} failed")

    # Verify
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=db) as session:
        r = session.run(
            "MATCH ()-[r:出演]->() RETURN type(r) AS type, count(r) AS cnt"
        ).single()
        print(f"出演 relationships now in DB: {r['cnt']}")
    driver.close()

if __name__ == "__main__":
    main()
