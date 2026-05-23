#!/usr/bin/env python3
"""Marvel Universe Graph Import to Neo4j Sandbox - 直接从 Cypher 文件导入"""
import re
from neo4j import GraphDatabase

DB_URL = "bolt://100.31.190.219:7687"
DB_PASSWORD = "others-combination-keyword"

def import_marvel_data():
    print("Connecting to Neo4j Sandbox...")
    driver = GraphDatabase.driver(DB_URL, auth=("neo4j", DB_PASSWORD))
    
    try:
        print("Clearing existing data...")
        with driver.session(database="neo4j") as session:
            session.run("MATCH (n) DETACH DELETE n")
        
        # Read Cypher file
        with open('marvel_graph_data/import_data.cypher', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换全角括号为半角括号（GQL 不识别全角括号作为字符串内容）
        content = content.replace('\uff08', '(').replace('\uff09', ')')
        
        # 修复关系语句中的中文关系标签引号问题
        # 原始格式: MERGE (c1)-[:成员]->(t1);
        # 这是正确的，不需要修改
        
        # Strip comments and blank lines
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
        
        print(f"Found {len(lines)} statements to execute")
        
        # Execute one by one (GQL 支持原始 MERGE 语句带中文)
        print("Importing...")
        with driver.session(database="neo4j") as session:
            success = 0
            failed = 0
            for i, line in enumerate(lines, 1):
                # Remove trailing semicolon if present
                stmt = line.rstrip(';')
                try:
                    session.run(stmt)
                    success += 1
                except Exception as e:
                    failed += 1
                    if failed <= 5:
                        err_msg = str(e)
                        # Get just the Neo4j error message
                        error_detail = err_msg[:200] if len(err_msg) > 200 else err_msg
                        print(f"  Fail #{i}: {error_detail}")
                        print(f"    {stmt[:150]}...")
        
        print(f"\n  {success}/{len(lines)} succeeded, {failed} failed")
        
        # Verify import
        print("\nVerifying...")
        with driver.session(database="neo4j") as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n) AS label, count(*) AS count
                ORDER BY count DESC
            """)
            print("\n=== Import Summary ===")
            for record in result:
                labels = record['label']
                if labels:
                    print(f"  {labels[0]}: {record['count']}")
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS rels")
            for record in result:
                print(f"  Relationships: {record['rels']}")
        
        # Show sample
        print("\n=== Sample Characters ===")
        with driver.session(database="neo4j") as session:
            result = session.run("MATCH (n:Character) RETURN n.name AS en, n.name_cn AS cn LIMIT 5")
            for record in result:
                print(f"  {record['en']}: {record['cn']}")
        
        print("\n✅ Import complete!")
        
    finally:
        driver.close()

if __name__ == '__main__':
    import_marvel_data()
