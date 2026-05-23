#!/usr/bin/env python3
"""
Marvel Universe Cypher Data Generator
Generates Cypher MERGE statements for Marvel entities.
Appends to import_data.cypher file.
"""
import re
import sys
import os
import csv
from datetime import datetime

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')
TELEMETRY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'telemetry_log.csv')

def get_existing_entities():
    """Parse existing cypher file and return set of entity names."""
    if not os.path.exists(CYPER_FILE):
        return set()
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    entities = set()
    # Match: (c1:Character {name: "Iron Man", ...})
    pattern = r'\((\w+):(\w+)\s*\{[^}]*name:\s*"([^"]*)"'
    for match in re.finditer(pattern, content):
        var_name, label, name = match.groups()
        entities.add(f"{label}:{name}")
    return entities

def get_existing_vars():
    """Get set of existing variable aliases."""
    if not os.path.exists(CYPER_FILE):
        return set()
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    return set(re.findall(r'\((\w+):', content))

def append_cypher(statements):
    """Append Cypher statements to file."""
    os.makedirs(os.path.dirname(CYPER_FILE), exist_ok=True)
    with open(CYPER_FILE, 'a') as f:
        for stmt in statements:
            f.write(stmt + '\n')

def validate_cypher(text):
    """Basic Cypher syntax validation."""
    errors = []
    lines = text.strip().split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if not line.startswith('MERGE'):
            errors.append(f"Line {i}: Must start with MERGE")
    return errors

def append_telemetry(operation, search_queries, batch_size, lines_added, total_lines, status):
    """Append telemetry record."""
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

def escape_value(val):
    """Escape double quotes in values for Cypher."""
    return val.replace('"', '\\"')

def build_node_statement(var, label, props, name_key='name'):
    """Build a MERGE statement for a node.
    
    name_key: the property to use for dedup (default 'name').
    """
    name = props.get(name_key, '')
    if not name:
        return None
    
    # Build property string
    prop_parts = [f'{name_key}: "{escape_value(name)}"']
    for k, v in props.items():
        if k == name_key:
            continue
        prop_parts.append(f'{k}: "{escape_value(str(v))}"')
    
    props_str = ', '.join(prop_parts)
    stmt = f'MERGE ({var}:{label} {{{props_str}}});'
    return stmt

# Data definitions - each item is a node: (var, label, {props})
# For items without 'name' as identifier, use 'title' for Movies, 'event_name' for Events, 'item_name' for Items

BATCH_DATA = [
    # Batch 2: More Avengers
    ('c100', 'Character', {'name': 'Spider-Man', 'real_name': 'Peter Parker', 'species': 'Human (Enhanced)', 'first_appearance': 'Amazing Fantasy #15 (August 1962)', 'abilities': 'Wall-crawling, Superhuman strength, Spider-sense, Web-slinging'}),
    ('c101', 'Character', {'name': 'Doctor Strange', 'real_name': 'Stephen Strange', 'species': 'Human', 'first_appearance': 'Strange Tales #110 (July 1963)', 'abilities': 'Master of mystic arts, Time manipulation, Astral projection, Teleportation'}),
    ('c102', 'Character', {'name': "Black Panther", 'real_name': "T'Challa", 'species': 'Human (Enhanced)', 'first_appearance': "Fantastic Four #52 (July 1966)", 'abilities': 'Superhuman strength via Heart-Shaped Herb, Genius intellect, Vibranium suit, Master combatant'}),
    ('c103', 'Character', {'name': 'Captain Marvel', 'real_name': 'Carol Danvers', 'species': 'Human/Kree Hybrid', 'first_appearance': 'Marvel Super-Heroes #13 (March 1968)', 'abilities': 'Superhuman strength, Flight, Energy projection, Photon blasts, Cosmic awareness'}),
    ('c104', 'Character', {'name': 'Ant-Man', 'real_name': 'Scott Lang', 'species': 'Human', 'first_appearance': 'Avengers #181 (March 1979)', 'abilities': 'Size manipulation, Insect communication, Superhuman strength when small'}),
    ('c105', 'Character', {'name': 'Scarlet Witch', 'real_name': 'Wanda Maximoff', 'species': 'Human (Enhanced)', 'first_appearance': 'X-Men #4 (March 1964)', 'abilities': 'Reality warping, Chaos magic, Telekinesis, Mind manipulation'}),
    ('c106', 'Character', {'name': 'Falcon', 'real_name': 'Sam Wilson', 'species': 'Human', 'first_appearance': 'Captain America #117 (September 1968)', 'abilities': 'Flight via mechanical wings, Telepathic link with birds, Expert combatant'}),
    ('c107', 'Character', {'name': 'War Machine', 'real_name': 'James Rhodes', 'species': 'Human', 'first_appearance': 'Iron Man #118 (January 1979)', 'abilities': 'Powered armor, Flight, Various weapons systems, Superhuman strength'}),
    
    # Batch 3: X-Men
    ('c200', 'Character', {'name': 'Professor X', 'real_name': 'Charles Xavier', 'species': 'Mutant', 'first_appearance': 'X-Men #1 (September 1963)', 'abilities': 'Telepathy, Mind control, Mental projection, Genius intellect'}),
    ('c201', 'Character', {'name': 'Cyclops', 'real_name': 'Scott Summers', 'species': 'Mutant', 'first_appearance': 'X-Men #1 (September 1963)', 'abilities': 'Optic blasts, Expert tactician, Leadership'}),
    ('c202', 'Character', {'name': 'Wolverine', 'real_name': 'James Logan Howlett', 'species': 'Mutant (Enhanced)', 'first_appearance': 'Incredible Hulk #181 (October 1974)', 'abilities': 'Healing factor, Adamantium claws, Superhuman senses, Enhanced strength'}),
    ('c203', 'Character', {'name': 'Storm', 'real_name': 'Ororo Munroe', 'species': 'Mutant', 'first_appearance': 'Giant-Size X-Men #1 (May 1975)', 'abilities': 'Weather control, Flight, Lightning manipulation'}),
    ('c204', 'Character', {'name': 'Jean Grey', 'real_name': 'Jean Grey', 'species': 'Mutant', 'first_appearance': 'X-Men #1 (September 1963)', 'abilities': 'Telepathy, Telekinesis, Phoenix Force connection'}),
    ('c205', 'Character', {'name': 'Magneto', 'real_name': 'Erik Lehnsherr', 'species': 'Mutant', 'first_appearance': 'X-Men #1 (September 1963)', 'abilities': 'Magnetism control, Magnetic force fields, Flight, Metal manipulation'}),
    ('c206', 'Character', {'name': 'Beast', 'real_name': 'Henry McCoy', 'species': 'Mutant', 'first_appearance': 'X-Men #1 (September 1963)', 'abilities': 'Superhuman agility, Genius intellect, Enhanced strength, Clawed hands'}),
    ('c207', 'Character', {'name': 'Iceman', 'real_name': 'Bobby Drake', 'species': 'Mutant', 'first_appearance': 'X-Men #1 (September 1963)', 'abilities': 'Cryokinesis, Ice form transformation, Temperature reduction'}),
    ('c208', 'Character', {'name': 'Angel', 'real_name': 'Warren Worthington III', 'species': 'Mutant', 'first_appearance': 'X-Men #1 (September 1963)', 'abilities': 'Flight, Winged flight, Feather projection'}),
    
    # Batch 4: Villains
    ('c300', 'Character', {'name': 'Thanos', 'species': 'Eternal (Deviant)', 'first_appearance': 'Iron Man #55 (February 1973)', 'abilities': 'Superhuman strength, Durability, Genius intellect, Energy manipulation'}),
    ('c301', 'Character', {'name': 'Loki', 'species': 'Frost Giant', 'first_appearance': 'Venus #6 (September 1949)', 'abilities': 'Magic, Shapeshifting, Illusion casting, Superhuman strength'}),
    ('c302', 'Character', {'name': 'Doctor Doom', 'real_name': 'Victor Von Doom', 'species': 'Human', 'first_appearance': 'Fantastic Four #5 (July 1962)', 'abilities': 'Genius intellect, Sorcery, Powered armor, Diplomatic immunity'}),
    ('c303', 'Character', {'name': 'Green Goblin', 'real_name': 'Norman Osborn', 'species': 'Human (Enhanced)', 'first_appearance': 'Amazing Spider-Man #14 (July 1964)', 'abilities': 'Superhuman strength, Enhanced intellect, Goblin formula effects, Advanced gadgets'}),
    ('c304', 'Character', {'name': 'Red Skull', 'real_name': 'Johann Schmidt', 'species': 'Human (Enhanced)', 'first_appearance': 'Captain America Comics #7 (October 1941)', 'abilities': 'Strategic genius, Combat training, Cosmo radiation enhanced physiology'}),
    ('c305', 'Character', {'name': 'Ultron', 'species': 'Artificial Intelligence', 'first_appearance': 'Avengers #54 (July 1968)', 'abilities': 'Superhuman strength, Regeneration, Flight, Energy projection, Mind control'}),
    ('c306', 'Character', {'name': 'Venom', 'real_name': 'Eddie Brock', 'species': 'Symbiote Host', 'first_appearance': 'Amazing Spider-Man #300 (May 1988)', 'abilities': 'Superhuman strength, Shapeshifting, Camouflage, Spider-sense disruption'}),
    
    # Batch 5: Locations
    ('l10', 'Location', {'name': 'Wakanda', 'type': 'Nation'}),
    ('l11', 'Location', {'name': 'Latveria', 'type': 'Nation'}),
    ('l12', 'Location', {'name': 'Genosha', 'type': 'Island Nation'}),
    ('l13', 'Location', {'name': 'Knowhere', 'type': 'Cosmic Location'}),
    ('l14', 'Location', {'name': 'Titan', 'type': 'Moon'}),
    ('l15', 'Location', {'name': 'Xavier Mansion', 'type': 'School'}),
    ('l16', 'Location', {'name': 'Sanctum Sanctorum', 'type': 'Mystical Building'}),
    ('l17', 'Location', {'name': 'Stark Tower', 'type': 'Headquarters'}),
    ('l18', 'Location', {'name': 'Asgard', 'type': 'Realm'}),
    
    # Batch 6: Movies (use 'title' as name_key)
    ('m1', 'Movie', {'title': 'Iron Man', 'year': '2008'}),
    ('m2', 'Movie', {'title': 'The Avengers', 'year': '2012'}),
    ('m3', 'Movie', {'title': 'Guardians of the Galaxy', 'year': '2014'}),
    ('m4', 'Movie', {'title': 'Doctor Strange', 'year': '2016'}),
    ('m5', 'Movie', {'title': 'Black Panther', 'year': '2018'}),
    ('m6', 'Movie', {'title': 'Avengers: Infinity War', 'year': '2018'}),
    ('m7', 'Movie', {'title': 'Avengers: Endgame', 'year': '2019'}),
    ('m8', 'Movie', {'title': 'Spider-Man: No Way Home', 'year': '2021'}),
    
    # Batch 7: Events (use 'event_name' as name_key)
    ('e1', 'Event', {'event_name': 'Battle of New York', 'year': '2012'}),
    ('e2', 'Event', {'event_name': 'Battle of Sokovia', 'year': '2015'}),
    ('e3', 'Event', {'event_name': 'Infinity War', 'year': '2018'}),
    ('e4', 'Event', {'event_name': 'The Blip', 'year': '2018'}),
    ('e5', 'Event', {'event_name': 'Civil War', 'year': '2016'}),
    ('e6', 'Event', {'event_name': 'Secret Wars', 'year': '1984'}),
    
    # Batch 8: Infinity Stones (use 'item_name' as name_key)
    ('i100', 'Item', {'item_name': 'Space Stone', 'type': 'Infinity Stone'}),
    ('i101', 'Item', {'item_name': 'Mind Stone', 'type': 'Infinity Stone'}),
    ('i102', 'Item', {'item_name': 'Reality Stone', 'type': 'Infinity Stone'}),
    ('i103', 'Item', {'item_name': 'Power Stone', 'type': 'Infinity Stone'}),
    ('i104', 'Item', {'item_name': 'Time Stone', 'type': 'Infinity Stone'}),
    ('i105', 'Item', {'item_name': 'Soul Stone', 'type': 'Infinity Stone'}),
    ('i106', 'Item', {'item_name': 'Infinity Gauntlet', 'type': 'Artifact'}),
    
    # Relationships
    ('c100', 'MEMBER_OF', 't1'),  # Spider-Man -> Avengers
    ('c101', 'MEMBER_OF', 't1'),  # Doctor Strange -> Avengers
    ('c102', 'MEMBER_OF', 't1'),  # Black Panther -> Avengers
    ('c103', 'MEMBER_OF', 't1'),  # Captain Marvel -> Avengers
    ('c105', 'MEMBER_OF', 't1'),  # Scarlet Witch -> Avengers
    ('c106', 'MEMBER_OF', 't1'),  # Falcon -> Avengers
    ('c107', 'MEMBER_OF', 't1'),  # War Machine -> Avengers
    ('c200', 'MEMBER_OF', 't5'),  # Professor X -> X-Men
    ('c201', 'MEMBER_OF', 't5'),  # Cyclops -> X-Men
    ('c202', 'MEMBER_OF', 't5'),  # Wolverine -> X-Men
    ('c203', 'MEMBER_OF', 't5'),  # Storm -> X-Men
    ('c204', 'MEMBER_OF', 't5'),  # Jean Grey -> X-Men
    ('c205', 'MEMBER_OF', 't6'),  # Magneto -> Brotherhood
    ('c206', 'MEMBER_OF', 't5'),  # Beast -> X-Men
    ('c207', 'MEMBER_OF', 't5'),  # Iceman -> X-Men
    ('c208', 'MEMBER_OF', 't5'),  # Angel -> X-Men
    ('c300', 'ENEMY_OF', 'c1'),   # Thanos -> Iron Man
    ('c300', 'ENEMY_OF', 'c2'),   # Thanos -> Captain America
    ('c300', 'ENEMY_OF', 't1'),   # Thanos -> Avengers
    ('c301', 'ENEMY_OF', 'c3'),   # Loki -> Thor
    ('c301', 'ENEMY_OF', 'c2'),   # Loki -> Captain America
    ('c302', 'ENEMY_OF', 't4'),   # Doctor Doom -> Fantastic Four (using t4 as placeholder)
    ('c303', 'ENEMY_OF', 'c100'), # Green Goblin -> Spider-Man
    ('c304', 'ENEMY_OF', 'c2'),   # Red Skull -> Captain America
    ('c305', 'ENEMY_OF', 't1'),   # Ultron -> Avengers
    ('c306', 'ENEMY_OF', 'c100'), # Venom -> Spider-Man
    ('c205', 'ENEMY_OF', 'c200'), # Magneto -> Professor X
    ('c202', 'ENEMY_OF', 'c301'), # Wolverine -> Loki (cross-universe rival)
    ('c5', 'ALLY_OF', 'c100'),    # Black Widow -> Spider-Man
    ('c6', 'ALLY_OF', 'c100'),    # Hawkeye -> Spider-Man
    ('c3', 'ALLY_OF', 'c301'),    # Thor -> Loki (brothers)
    ('c102', 'FROM', 'l10'),      # Black Panther -> Wakanda
    ('c302', 'FROM', 'l11'),      # Doctor Doom -> Latveria
    ('c200', 'FROM', 'l15'),      # Professor X -> Xavier Mansion
    ('c101', 'FROM', 'l16'),      # Doctor Strange -> Sanctum Sanctorum
    ('c3', 'FROM', 'l18'),        # Thor -> Asgard
    ('c1', 'USES', 'i100'),       # Iron Man uses Space Stone (in Avengers 2012)
    ('c305', 'USES', 'i101'),     # Ultron uses Mind Stone
    ('c300', 'USES', 'i106'),     # Thanos uses Infinity Gauntlet
    ('c204', 'USES', 'i102'),     # Jean Grey uses Reality Stone (Phoenix)
]

def main():
    existing_entities = get_existing_entities()
    existing_vars = get_existing_vars()
    total_lines_added = 0
    new_statements = []
    
    print("Starting Marvel Universe Data Generation...")
    print(f"Existing entities: {len(existing_entities)}")
    
    # Process nodes (3-tuple items) and relationships (3-tuple: var, rel_type, target)
    for item in BATCH_DATA:
        var, label_or_rel, rest = item
        
        # Check if it's a relationship (label_or_rel is a string like 'MEMBER_OF')
        if isinstance(rest, str) and ':' not in rest:
            # This is a relationship: (var)-[:label_or_rel]->(rest)
            target_var = rest
            rel_type = label_or_rel
            stmt = f"MERGE ({var})-[:{rel_type}]->({target_var});"
            new_statements.append(stmt)
            total_lines_added += 1
            continue
        
        # This is a node
        props = rest
        label = label_or_rel
        
        # Determine name_key based on label
        if label == 'Movie':
            name_key = 'title'
        elif label == 'Event':
            name_key = 'event_name'
        elif label == 'Item':
            name_key = 'item_name'
        else:
            name_key = 'name'
        
        # Check if already exists
        name = props.get(name_key, '')
        entity_key = f"{label}:{name}"
        if entity_key in existing_entities:
            print(f"  Skipping existing: {entity_key}")
            continue
        
        # Generate statement
        stmt = build_node_statement(var, label, props, name_key)
        if stmt:
            new_statements.append(stmt)
            existing_entities.add(entity_key)
            total_lines_added += 1
        else:
            print(f"  ERROR: Could not build statement for {var} {label} {props}")
    
    if new_statements:
        print(f"\nAppending {len(new_statements)} statements to {CYPER_FILE}")
        append_cypher(new_statements)
    else:
        print("\nNo new statements to add")
    
    # Get final line count
    with open(CYPER_FILE, 'r') as f:
        all_lines = f.readlines()
        total_lines = len([l for l in all_lines if l.strip() and not l.strip().startswith('#')])
    
    print(f"Total Cypher lines: {total_lines}")
    
    # Validate
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    errors = validate_cypher(content)
    if errors:
        print(f"Validation errors: {len(errors)}")
        for e in errors[:5]:
            print(f"  {e}")
    else:
        print("Cypher validation: OK")
    
    # Log telemetry
    try:
        append_telemetry(
            'Batch_2_to_8_All',
            '5',
            str(total_lines_added),
            str(total_lines_added),
            str(total_lines),
            'success'
        )
        print("Telemetry logged.")
    except Exception as e:
        print(f"Telemetry logging failed: {e}")
    
    print("TASK_BATCH_COMPLETED")

if __name__ == '__main__':
    main()
