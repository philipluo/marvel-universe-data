#!/usr/bin/env python3
"""Final pass: translate remaining English fields."""
import re
import os

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')

# Remaining species
REMAINING_SPECIES = {
    '人类 (Enhanced)': '人类（强化）',
    '人类 (Gamma Mutate)': '人类（伽马突变）',
}

# Remaining abilities
REMAINING_ABILITIES = {
    'Genius intellect': '天才智力',
    'Genius intelligence': '天才智力',
    'Martial arts': '武术',
    'Energy manipulation': '能量操控',
    'Cosmic power': '宇宙之力',
    'Weapon mastery': '武器大师',
    'Peak human conditioning': '人类体能巅峰',
    'Master martial artist': '武术大师',
    'Tactical genius': '战术天才',
    'Scientific innovation': '科学创新',
    'Pym particles': '皮姆粒子',
    'Human/Cosmic Entity': '人类/宇宙实体',
    'Mutant/': '变种人（',
}

# Item names (first batch)
ITEM_NAME_FIRST = {
    'Vibranium Shield': '振金盾牌',
    'Mjolnir': '妙尔尼尔（雷神之锤）',
    'Iron Man Armor': '钢铁侠战甲',
    'Arc Reactor': '弧反应堆',
    "Widow's Bite": '寡妇之吻',
    'Hawkeye Bow': '鹰眼弓',
    'Trick Arrows': '特制箭矢',
}

# Item type remaining
ITEM_TYPE_REMAINING = {
    'Ammunition': '弹药',
}

# Team type remaining
TEAM_TYPE_REMAINING = {
    'Mutant Team': '变种人团队',
}

def main():
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    
    changes = 0
    
    # Species
    for eng, cn in REMAINING_SPECIES.items():
        if eng in content:
            content = content.replace(f'species: "{eng}"', f'species: "{cn}"')
            changes += 1
    
    # Abilities
    for eng, cn in REMAINING_ABILITIES.items():
        content = content.replace(eng, cn)
        changes += 1
    
    # Item names (first batch)
    for eng, cn in ITEM_NAME_FIRST.items():
        content = content.replace(f'name: "{eng}"', f'name: "{cn}"')
        changes += 1
    
    # Item types
    for eng, cn in ITEM_TYPE_REMAINING.items():
        content = content.replace(f'type: "{eng}"', f'type: "{cn}"')
        changes += 1
    
    # Team types
    for eng, cn in TEAM_TYPE_REMAINING.items():
        content = content.replace(f'type: "{eng}"', f'type: "{cn}"')
        changes += 1
    
    with open(CYPER_FILE, 'w') as f:
        f.write(content)
    
    print(f"Final translation done! Changes: {changes}")
    
    # Verify no more English in key fields
    print("\n=== Species check ===")
    species = re.findall(r'species: "([^"]*)"', content)
    for s in set(species):
        print(f"  {s}")
    
    print("\n=== Abilities check (any remaining English?) ===")
    abils = re.findall(r'abilities: "([^"]*)"', content)
    for a in abils[:5]:
        print(f"  {a[:80]}")
    
    print("\n=== Items check ===")
    items = re.findall(r'Item \{name: "([^"]*)"', content)
    for i in items:
        print(f"  {i}")
    
    # Count
    chars = len(re.findall(r':Character \{name:', content))
    with_cn = len(re.findall(r'name_cn:', content))
    total_lines = len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')])
    rels = len(re.findall(r'\]->', content))
    
    print(f"\n=== Final Stats ===")
    print(f"Characters: {chars} (with cn: {with_cn})")
    print(f"Total non-comment lines: {total_lines}")
    print(f"Relationships: {rels}")

if __name__ == '__main__':
    main()
