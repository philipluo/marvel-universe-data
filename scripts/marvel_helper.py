#!/usr/bin/env python3
"""
Marvel Universe Cypher Data Helper
- Parse existing .cypher file to extract collected entities (dedup)
- Validate Cypher syntax before appending
- Report statistics
"""
import re
import sys
import os
import csv
from datetime import datetime

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')
TELEMETRY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'telemetry_log.csv')

def parse_cypher_entities(cypher_text):
    """Extract all entity names and labels from MERGE statements."""
    entities = {}
    # Match patterns like (c1:Character {name: "Iron Man", ...})
    # and (t1:Team {name: "Avengers"})
    pattern = r'\((\w+):(\w+)\s*\{[^}]*name:\s*"([^"]*)"'
    for match in re.finditer(pattern, cypher_text):
        var_name, label, name = match.groups()
        key = f"{label}:{name}"
        entities[key] = var_name
    
    # Also match entities without properties like (c1:Character)
    # Less common but possible
    return entities

def get_collected_names(cypher_text):
    """Return set of all collected entity names."""
    entities = parse_cypher_entities(cypher_text)
    return set(entities.keys())

def get_collected_by_label(cypher_text):
    """Return dict of label -> set of names."""
    entities = parse_cypher_entities(cypher_text)
    by_label = {}
    for key in entities:
        label, name = key.split(':', 1)
        by_label.setdefault(label, set()).add(name)
    return by_label

def validate_cypher(text):
    """Basic Cypher syntax validation."""
    errors = []
    lines = text.strip().split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Must start with MERGE
        if not line.startswith('MERGE'):
            errors.append(f"Line {i}: Must start with MERGE, got: {line[:50]}")
        # Check for unescaped quotes
        if re.search(r'"[^"\\]*(?:\\.[^"\\]*)*"', line) is None and '"' in line:
            errors.append(f"Line {i}: Possible unescaped quote")
    return errors

def count_cypher_lines(cypher_text):
    """Count non-empty, non-comment lines."""
    lines = [l for l in cypher_text.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
    return len(lines)

def append_telemetry(operation, search_queries, batch_size, lines_added, total_lines, status):
    """Append a telemetry record."""
    os.makedirs(os.path.dirname(TELEMETRY_FILE), exist_ok=True)
    file_exists = os.path.exists(TELEMETRY_FILE)
    with open(TELEMETRY_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'operation', 'search_queries', 'batch_size', 'cypher_lines_added', 'total_cypher_lines', 'status'])
        writer.writerow([
            datetime.utcnow().isoformat(),
            operation,
            search_queries,
            batch_size,
            lines_added,
            total_lines,
            status
        ])

def main():
    if len(sys.argv) < 2:
        print("Usage: python marvel_helper.py [status|dedup|validate|telemetry]")
        print("  status   - Show collection statistics")
        print("  dedup    - List collected entities")
        print("  validate <file> - Validate Cypher syntax")
        print("  telemetry <op> <queries> <batch> <added> <total> <status> - Log telemetry")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if not os.path.exists(CYPER_FILE):
        if cmd == 'status':
            print("No data collected yet.")
            return
        print(f"No cypher file found at {CYPER_FILE}")
        sys.exit(1)
    
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    
    if cmd == 'status':
        by_label = get_collected_by_label(content)
        total = sum(len(names) for names in by_label.values())
        print(f"Total entities: {total}")
        print(f"Cypher lines: {count_cypher_lines(content)}")
        for label, names in sorted(by_label.items()):
            print(f"  {label}: {len(names)}")
    
    elif cmd == 'dedup':
        collected = get_collected_names(content)
        for item in sorted(collected):
            print(item)
    
    elif cmd == 'validate':
        if len(sys.argv) < 3:
            print("Usage: python marvel_helper.py validate <file>")
            sys.exit(1)
        with open(sys.argv[2], 'r') as f:
            text = f.read()
        errors = validate_cypher(text)
        if errors:
            print(f"Validation errors ({len(errors)}):")
            for e in errors:
                print(f"  {e}")
            sys.exit(1)
        else:
            print("Cypher syntax OK")
    
    elif cmd == 'telemetry':
        if len(sys.argv) < 8:
            print("Usage: python marvel_helper.py telemetry <op> <queries> <batch> <added> <total> <status>")
            sys.exit(1)
        append_telemetry(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
        print("Telemetry logged")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
