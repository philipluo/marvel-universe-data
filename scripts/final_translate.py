#!/usr/bin/env python3
"""Last cleanup for remaining English."""
import re
import os

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')

# Final translation maps
REMAINING = {
    # Species
    ' 泽恩-沃伯里人': '泽恩-沃伯里人',
    
    # Item types
    'Space Stone Container': '空间宝石容器',
    'Infinity Stone Container': '无限宝石容器',
    'Infinity Artifact': '无限神器',
    
    # Abilities
    'Weapon master': '武器大师',
    'Peak human': '人类巅峰',
    'Military training': '军事训练',
    'Master assassin': '刺客大师',
    'Enhanced speed': '强化速度',
    'Combat training': '战斗训练',
    'Business acumen': '商业敏锐',
    'Body manipulation': '身体操控',
    'Yaka arrow control': '亚卡箭操控',
    'Weapons master': '武器大师',
}

def main():
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    
    changes = 0
    for eng, cn in REMAINING.items():
        if eng in content:
            content = content.replace(eng, cn)
            changes += 1
            print(f"  Replaced: '{eng}' -> '{cn}'")
    
    with open(CYPER_FILE, 'w') as f:
        f.write(content)
    
    print(f"\nDone! {changes} replacements")
    
    # Verify items
    print("\n=== Items (full) ===")
    for m in re.finditer(r'MERGE \(\w+:Item \{[^}]+\}\);', content):
        print(m.group(0)[:120])
    
    # Verify team types
    print("\n=== Team types ===")
    for m in re.finditer(r'MERGE \(\w+:Team \{name: "([^"]+)", type: "([^"]+)"\}\);', content):
        print(f"  {m.group(1)}: {m.group(2)}")
    
    # Final stats
    chars = len(re.findall(r':Character \{name:', content))
    lines = len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')])
    print(f"\nCharacters: {chars}")
    print(f"Total lines: {lines}")

if __name__ == '__main__':
    main()
