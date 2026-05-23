#!/usr/bin/env python3
"""Final cleanup: fix all mixed EN/CN text."""
import re
import os

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')

MIXED_TEXT = {
    '人类/Reptile Hybrid': '人类/爬行动物混血',
    'Vampire-人类 Hybrid': '吸血鬼-人类混血',
    '人类/Celestial Hybrid': '人类/天神族混血',
    '人类 (Demon Bond)': '人类（恶魔契约）',
    '人类 (Silicate)': '人类（硅基）',
    '人类 (Rock-like)': '人类（岩石形态）',
    '变种人 (Enhanced)': '变种人（强化）',
    '变种人/Cyborg': '变种人/改造',
    '人类 (Gamma Mutate)': '人类（伽马突变）',
    '人类 (Enhanced)': '人类（强化）',
    'zen-Whoberian': '泽恩-沃伯里人',
    'Kree': '克里人',
    '多种': '多种',
}

ABILITY_MIXED = {
    'via Mjolnir': '（妙尔尼尔）',
    'via Heart-Shaped Herb': '（心形草）',
}

def main():
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    
    changes = 0
    for eng, cn in MIXED_TEXT.items():
        if eng in content:
            content = content.replace(eng, cn)
            changes += 1
    
    for eng, cn in ABILITY_MIXED.items():
        content = content.replace(eng, cn)
        changes += 1
    
    with open(CYPER_FILE, 'w') as f:
        f.write(content)
    
    print(f"Cleanup done! Changes: {changes}")
    
    # Final verification
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    
    # Check for any remaining mixed text patterns
    print("\n=== Checking for remaining English in character fields ===")
    for m in re.finditer(r':Character \{([^}]+)\}', content):
        props = m.group(1)
        # Check for patterns like "Enhanced)", "Hybrid", etc mixed in
        if re.search(r'\b[A-Z][a-z]+ [a-z]+ \([A-Z]', props):
            # Has capital letter mixed - likely remaining English
            name_m = re.search(r'name_cn: "([^"]*)"', props)
            if name_m:
                print(f"  {name_m.group(1)}: {props[:100]}")
    
    print("\n=== Species list (final) ===")
    species = re.findall(r'species: "([^"]*)"', content)
    for s in sorted(set(species)):
        print(f"  {s}")
    
    print("\n=== 10 Sample Characters (full line) ===")
    chars_found = 0
    for m in re.finditer(r'MERGE \(\w+:Character \{[^}]+\}\);', content):
        if chars_found < 10:
            print(m.group(0)[:130] + '...')
            chars_found += 1

if __name__ == '__main__':
    main()
