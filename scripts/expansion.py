#!/usr/bin/env python3
"""
Marvel Universe Data Expansion Script
Adds 80+ characters, relationships, movies, events, locations
"""
import re
import os
import csv
from datetime import datetime, timezone

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')
TELEMETRY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'telemetry_log.csv')

def get_existing_entities():
    if not os.path.exists(CYPER_FILE):
        return set()
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    entities = set()
    # Match both name: and title: and event_name: and item_name:
    for match in re.finditer(r'\((\w+):(\w+)\s*\{[^}]*name:\s*"([^"]*)"', content):
        entities.add(f"{match.group(2)}:{match.group(3)}")
    for match in re.finditer(r'\((\w+):(\w+)\s*\{[^}]*title:\s*"([^"]*)"', content):
        entities.add(f"{match.group(2)}:{match.group(3)}")
    for match in re.finditer(r'\((\w+):(\w+)\s*\{[^}]*event_name:\s*"([^"]*)"', content):
        entities.add(f"{match.group(2)}:{match.group(3)}")
    for match in re.finditer(r'\((\w+):(\w+)\s*\{[^}]*item_name:\s*"([^"]*)"', content):
        entities.add(f"{match.group(2)}:{match.group(3)}")
    return entities

def escape_val(val):
    return str(val).replace('"', '\\"')

def build_node(var, label, props, name_key='name'):
    name = props.get(name_key, '')
    if not name:
        return None
    parts = [f'{name_key}: "{escape_val(name)}"']
    for k, v in props.items():
        if k == name_key:
            continue
        parts.append(f'{k}: "{escape_val(v)}"')
    return f'MERGE ({var}:{label} {{{", ".join(parts)}}});'

# ===== NEW DATA =====
NEW_CHARS = [
    # === Guardians of the Galaxy ===
    ('c400', 'Character', {'name': 'Star-Lord', 'real_name': 'Peter Quill', 'species': 'Human/Celestial Hybrid', 'first_appearance': 'Marvel Preview #4 (October 1976)', 'abilities': 'Expert marksman, Master tactician, Enhanced durability, Jet boots'}),
    ('c401', 'Character', {'name': 'Gamora', 'real_name': 'Gamora Zen-Whoberi', 'species': 'Zen-Whoberian', 'first_appearance': 'Strange Tales #180 (March 1975)', 'abilities': 'Superhuman strength, Agility, Healing factor, Master assassin, Swordsmanship'}),
    ('c402', 'Character', {'name': 'Drax', 'real_name': 'Drax the Destroyer', 'species': 'Human (Enhanced)', 'first_appearance': 'Invincible Iron Man #54 (March 1973)', 'abilities': 'Superhuman strength, Durability, Expert warrior, Regeneration'}),
    ('c403', 'Character', {'name': 'Rocket Raccoon', 'real_name': 'Rocket', 'species': 'Genetically Engineered Raccoon', 'first_appearance': 'Marvel Preview #7 (January 1976)', 'abilities': 'Genius intellect, Expert marksman, Tactical genius, Weapon master'}),
    ('c404', 'Character', {'name': 'Groot', 'real_name': 'Groot', 'species': 'Flora Colossus', 'first_appearance': 'Tales to Astonish #13 (November 1960)', 'abilities': 'Superhuman strength, Regeneration, Body manipulation, Plant control'}),
    ('c405', 'Character', {'name': 'Mantis', 'real_name': 'Mantis', 'species': 'Human (Enhanced)', 'first_appearance': 'Avengers #111 (February 1973)', 'abilities': 'Empathy, Emotion manipulation, Sleep induction, Martial arts'}),
    ('c406', 'Character', {'name': 'Nebula', 'real_name': 'Nebula', 'species': 'Luphomoid', 'first_appearance': 'Avengers Annual #12 (1983)', 'abilities': 'Cybernetic enhancements, Superhuman strength, Expert combatant, Shapeshifting'}),
    
    # === Fantastic Four ===
    ('c500', 'Character', {'name': 'Mister Fantastic', 'real_name': 'Reed Richards', 'species': 'Human (Enhanced)', 'first_appearance': 'Fantastic Four #1 (November 1961)', 'abilities': 'Genius intellect, Elasticity, Stretching, Scientific genius'}),
    ('c501', 'Character', {'name': 'Invisible Woman', 'real_name': 'Susan Storm', 'species': 'Human (Enhanced)', 'first_appearance': 'Fantastic Four #1 (November 1961)', 'abilities': 'Invisibility, Force fields, Energy projection'}),
    ('c502', 'Character', {'name': 'Human Torch', 'real_name': 'Johnny Storm', 'species': 'Human (Enhanced)', 'first_appearance': 'Fantastic Four #1 (November 1961)', 'abilities': 'Pyrokinesis, Flight, Fire manipulation, Invulnerability'}),
    ('c503', 'Character', {'name': 'The Thing', 'real_name': 'Ben Grimm', 'species': 'Human (Rock-like)', 'first_appearance': 'Fantastic Four #1 (November 1961)', 'abilities': 'Superhuman strength, Rock-like skin, Durability, Brawling'}),
    
    # === Additional Spider-Man allies/villains ===
    ('c600', 'Character', {'name': 'Mary Jane Watson', 'real_name': 'Mary Jane Watson', 'species': 'Human', 'first_appearance': 'Amazing Spider-Man #25 (April 1965)', 'abilities': 'Acting, Photography, Social skills'}),
    ('c601', 'Character', {'name': 'J. Jonah Jameson', 'real_name': 'John Jonah Jameson', 'species': 'Human', 'first_appearance': 'Amazing Spider-Man #1 (March 1963)', 'abilities': 'Media mogul, Business acumen'}),
    ('c602', 'Character', {'name': 'Doc Ock', 'real_name': 'Otto Octavius', 'species': 'Human (Enhanced)', 'first_appearance': 'Amazing Spider-Man #3 (July 1963)', 'abilities': 'Genius intellect, Mechanical tentacles, Superhuman strength via apparatus'}),
    ('c603', 'Character', {'name': 'Sandman', 'real_name': 'Flint Marko', 'species': 'Human (Silicate)', 'first_appearance': 'Amazing Spider-Man #4 (August 1963)', 'abilities': 'Body manipulation, Sand form, Superhuman strength, Regeneration'}),
    ('c604', 'Character', {'name': 'Electro', 'real_name': 'Max Dillon', 'species': 'Human (Enhanced)', 'first_appearance': 'Amazing Spider-Man #9 (February 1964)', 'abilities': 'Electricity generation, Energy absorption, Flight via electricity'}),
    ('c605', 'Character', {'name': 'Lizard', 'real_name': 'Curt Connors', 'species': 'Human/Reptile Hybrid', 'first_appearance': 'Amazing Spider-Man #6 (September 1963)', 'abilities': 'Superhuman strength, Regeneration, Tail, Prehistoric instincts'}),
    ('c606', 'Character', {'name': 'Vulture', 'real_name': 'Adrian Toomes', 'species': 'Human (Enhanced)', 'first_appearance': 'Amazing Spider-Man #2 (July 1963)', 'abilities': 'Flight via wing suit, Genius intellect, Scavenger technology'}),
    ('c607', 'Character', {'name': 'Kingpin', 'real_name': 'Wilson Fisk', 'species': 'Human', 'first_appearance': 'Amazing Spider-Man #50 (July 1967)', 'abilities': 'Peak human strength, Criminal mastermind, Political influence'}),
    ('c608', 'Character', {'name': 'Punisher', 'real_name': 'Frank Castle', 'species': 'Human', 'first_appearance': 'Amazing Spider-Man #129 (February 1974)', 'abilities': 'Expert marksman, Military training, Tactical genius, Weapons master'}),
    ('c609', 'Character', {'name': 'Daredevil', 'real_name': 'Matt Murdock', 'species': 'Human (Enhanced)', 'first_appearance': 'Daredevil #1 (April 1964)', 'abilities': 'Radar sense, Enhanced senses, Master martial artist, Acrobatics'}),
    ('c610', 'Character', {'name': 'Elektra', 'real_name': 'Elektra Natchios', 'species': 'Human (Enhanced)', 'first_appearance': 'Daredevil #168 (January 1981)', 'abilities': 'Master assassin, Swordsmanship, Martial arts, Stealth'}),
    
    # === X-Men expanded ===
    ('c700', 'Character', {'name': 'Rogue', 'real_name': 'Anna Marie', 'species': 'Mutant', 'first_appearance': 'Avengers Annual #10 (1981)', 'abilities': 'Power absorption, Superhuman strength, Flight, Life force drain'}),
    ('c701', 'Character', {'name': 'Gambit', 'real_name': 'Remy LeBeau', 'species': 'Mutant', 'first_appearance': 'Uncanny X-Men Annual #14 (1990)', 'abilities': 'Kinetic energy charging, Cards, Martial arts, Charisma'}),
    ('c702', 'Character', {'name': 'Colossus', 'real_name': 'Piotr Rasputin', 'species': 'Mutant', 'first_appearance': 'Giant-Size X-Men #1 (May 1975)', 'abilities': 'Organic steel transformation, Superhuman strength, Durability'}),
    ('c703', 'Character', {'name': 'Nightcrawler', 'real_name': 'Kurt Wagner', 'species': 'Mutant', 'first_appearance': 'Giant-Size X-Men #1 (May 1975)', 'abilities': 'Teleportation, Acrobatics, Prehensile tail, Stealth'}),
    ('c704', 'Character', {'name': 'Psylocke', 'real_name': 'Betsy Braddock', 'species': 'Mutant', 'first_appearance': 'Captain Britain #8 (July 1976)', 'abilities': 'Telepathy, Psionic blade, Martial arts, Ninja training'}),
    ('c705', 'Character', {'name': 'Cable', 'real_name': 'Nathan Summers', 'species': 'Mutant/Cyborg', 'first_appearance': 'New Mutants #87 (February 1990)', 'abilities': 'Telepathy, Telekinesis, Cyborg enhancements, Weapon master, Time travel'}),
    ('c706', 'Character', {'name': 'Storm', 'real_name': 'Ororo Munroe', 'species': 'Mutant', 'first_appearance': 'Giant-Size X-Men #1 (May 1975)', 'abilities': 'Weather control, Flight, Lightning manipulation', 'note': 'duplicate_check'}),
    ('c707', 'Character', {'name': 'Emma Frost', 'real_name': 'Emma Frost', 'species': 'Mutant', 'first_appearance': 'X-Men #93 (July 1976)', 'abilities': 'Telepathy, Diamond form, Mental domination'}),
    ('c708', 'Character', {'name': 'Sabretooth', 'real_name': 'Victor Creed', 'species': 'Mutant', 'first_appearance': 'Iron Fist #14 (August 1977)', 'abilities': 'Enhanced senses, Healing factor, Claws, Superhuman strength'}),
    ('c709', 'Character', {'name': 'Apocalypse', 'real_name': 'En Sabah Nur', 'species': 'Mutant', 'first_appearance': 'X-Factor #5 (June 1986)', 'abilities': 'Molecular manipulation, Shapeshifting, Superhuman strength, Immortality'}),
    
    # === More Avengers ===
    ('c800', 'Character', {'name': 'Winter Soldier', 'real_name': 'Bucky Barnes', 'species': 'Human (Enhanced)', 'first_appearance': 'Captain America Comics #1 (March 1941)', 'abilities': 'Expert marksman, Cybernetic arm, Martial arts, Assassin training'}),
    ('c801', 'Character', {'name': 'Scarlet Witch', 'real_name': 'Wanda Maximoff', 'species': 'Mutant', 'first_appearance': 'X-Men #4 (March 1964)', 'abilities': 'Reality warping, Chaos magic, Hex bolts', 'note': 'duplicate_check'}),
    ('c802', 'Character', {'name': 'Quicksilver', 'real_name': 'Pietro Maximoff', 'species': 'Mutant', 'first_appearance': 'X-Men #4 (March 1964)', 'abilities': 'Superhuman speed, Reflexes, Accelerated healing'}),
    ('c803', 'Character', {'name': 'Hercules', 'real_name': 'Hercules Panhellenios', 'species': 'Olympian God', 'first_appearance': 'Captain America #102 (October 1965)', 'abilities': 'Godlike strength, Invulnerability, Weapon mastery, Immortality'}),
    ('c804', 'Character', {'name': 'Shang-Chi', 'real_name': 'Shang-Chi', 'species': 'Human', 'first_appearance': 'Special Marvel Edition #15 (December 1973)', 'abilities': 'Master martial artist, Chi manipulation, Expert combatant'}),
    ('c805', 'Character', {'name': 'Blade', 'real_name': 'Eric Brooks', 'species': 'Vampire-Human Hybrid', 'first_appearance': 'Tomb of Dracula #10 (July 1973)', 'abilities': 'Vampire strengths, Solar absorption, Swordsmanship, Immunity to vampire weaknesses'}),
    ('c806', 'Character', {'name': 'Ghost Rider', 'real_name': 'Johnny Blaze', 'species': 'Human (Demon Bond)', 'first_appearance': 'Marvel Spotlight #5 (August 1972)', 'abilities': 'Hellfire, Penance stare, Supernatural strength, Motorcycle transformation'}),
    ('c807', 'Character', {'name': 'Invisible Woman', 'real_name': 'Sue Storm', 'species': 'Human (Enhanced)', 'first_appearance': 'Fantastic Four #1 (November 1961)', 'abilities': 'Invisibility, Force fields', 'note': 'duplicate_check'}),
    
    # === Cosmic Characters ===
    ('c900', 'Character', {'name': 'Captain Universe', 'real_name': 'Various', 'species': 'Cosmic Entity Host', 'first_appearance': 'Fantastic Four #1 (April 1965)', 'abilities': 'Cosmic powers, Energy manipulation, Flight, Superhuman strength'}),
    ('c901', 'Character', {'name': 'Silver Surfer', 'real_name': 'Norrin Radd', 'species': 'Human/Cosmic Entity', 'first_appearance': 'Fantastic Four #48 (March 1966)', 'abilities': 'Cosmic power surfing, Energy manipulation, Flight, Negate physiology'}),
    ('c902', 'Character', {'name': 'Galactus', 'real_name': 'Galan', 'species': 'Cosmic Entity', 'first_appearance': 'Fantastic Four #48 (March 1966)', 'abilities': 'Cosmic power, Matter manipulation, Planet devouring, Near-omnipotence'}),
    ('c903', 'Character', {'name': 'Heralds of Galactus', 'real_name': 'Various', 'species': 'Various', 'first_appearance': 'Fantastic Four #48 (March 1966)', 'abilities': 'Cosmic powers, Surfing, Energy manipulation'}),
    
    # === Heroes for Hire & Street Level ===
    ('c910', 'Character', {'name': 'Luke Cage', 'real_name': 'Carl Lucas', 'species': 'Human (Enhanced)', 'first_appearance': 'Heroes for Hire #1 (June 1972)', 'abilities': 'Superhuman strength, Unbreakable skin, Regeneration, Martial arts'}),
    ('c911', 'Character', {'name': 'Iron Fist', 'real_name': 'Danny Rand', 'species': 'Human (Enhanced)', 'first_appearance': 'Marvel Preview #15 (January 1977)', 'abilities': 'Chi power, Iron Fist strike, Martial arts master, Healing'}),
    ('c912', 'Character', {'name': 'Jessica Jones', 'real_name': 'Jessica Campbell Jones', 'species': 'Human (Enhanced)', 'first_appearance': 'Alias #1 (October 2001)', 'abilities': 'Superhuman strength, Flight, Detective skills, Telepathy resistance'}),
    ('c913', 'Character', {'name': 'Moon Knight', 'real_name': 'Marc Spector', 'species': 'Human (Enhanced)', 'first_appearance': 'Werewolf by Night #32 (October 1975)', 'abilities': 'Peak human conditioning, Martial arts, Crescent weapons, Multiple personalities'}),
    ('c914', 'Character', {'name': 'Shuri', 'real_name': "Shuri", 'species': 'Human', 'first_appearance': "Black Panther #2 (February 2005)", 'abilities': 'Genius intellect, Technopath, Vibranium technology, Scientific innovation'}),
    ('c915', 'Character', {'name': 'Okoye', 'real_name': 'Okoye', 'species': 'Human', 'first_appearance': "Black Panther #1 (January 1998)", 'abilities': 'Master martial artist, Spear wielder, Strategic genius, Dora Milaje leader'}),
    
    # === Villains expanded ===
    ('c920', 'Character', {'name': 'Kingpin', 'real_name': 'Wilson Fisk', 'species': 'Human', 'first_appearance': 'Amazing Spider-Man #50 (July 1967)', 'abilities': 'Peak human strength, Criminal mastermind', 'note': 'duplicate_check'}),
    ('c921', 'Character', {'name': 'Carnage', 'real_name': 'Cletus Kasady', 'species': 'Symbiote Host', 'first_appearance': 'Amazing Spider-Man #361 (April 1993)', 'abilities': 'Superhuman strength, Shapeshifting, Weapon generation, Regeneration'}),
    ('c922', 'Character', {'name': 'Mysterio', 'real_name': 'Quentin Beck', 'species': 'Human', 'first_appearance': 'Amazing Spider-Man #13 (May 1964)', 'abilities': 'Special effects mastery, Illusion creation, Drone control, Deception'}),
    ('c923', 'Character', {'name': 'Mandarin', 'real_name': 'Kang the Conqueror', 'species': 'Human (Enhanced)', 'first_appearance': 'Tales of Suspense #50 (March 1964)', 'abilities': 'Ten Ring mastery, Immortality, Energy projection, Combat expertise'}),
    
    # === Young Avengers & New Gen ===
    ('c930', 'Character', {'name': 'Hawkeye (Kate Bishop)', 'real_name': 'Kate Bishop', 'species': 'Human', 'first_appearance': 'Young Avengers #1 (October 2005)', 'abilities': 'Master archer, Fencing, Hand-to-hand combat, Genius-level intellect'}),
    ('c931', 'Character', {'name': 'Wiccan', 'real_name': 'William Kaplan', 'species': 'Mutant', 'first_appearance': 'Young Avengers #1 (October 2005)', 'abilities': 'Reality warping, Magic, Chaos magic, Spellcasting'}),
    ('c932', 'Character', {'name': 'Speed', 'real_name': 'Thomas Maximoff', 'species': 'Mutant', 'first_appearance': 'Young Avengers #2 (November 2005)', 'abilities': 'Superhuman speed, Enhanced reflexes, Speed force connection'}),
    ('c933', 'Character', {'name': 'Stature', 'real_name': 'Cassie Lang', 'species': 'Human (Enhanced)', 'first_appearance': 'Young Avengers #1 (October 2005)', 'abilities': 'Size manipulation, Shrinking, Pym particles'}),
    ('c934', 'Character', {'name': 'Ned Leeds', 'real_name': 'Eddie Brock', 'species': 'Human', 'first_appearance': 'Amazing Spider-Man #1 (April 1963)', 'abilities': 'Tech genius, Loyalty, Photography'}),
    
    # === Aliens & Cosmic ===
    ('c940', 'Character', {'name': 'Thanos', 'species': 'Eternal/Deviant Hybrid', 'first_appearance': 'Iron Man #55 (February 1973)', 'abilities': 'Superhuman strength, Energy manipulation, Immortality, Genius intellect', 'note': 'duplicate_check'}),
    ('c941', 'Character', {'name': 'Ronan', 'real_name': 'Ronan the Accuser', 'species': 'Kree', 'first_appearance': 'Fantastic Four #65 (February 1966)', 'abilities': 'Cosmic awareness, Hammer mastery, Kree technology, Accuser training'}),
    ('c942', 'Character', {'name': 'Yondu', 'real_name': 'Yondu Udonta', 'species': 'Centaurian', 'first_appearance': 'Marvel Super-Heroes #18 (January 1969)', 'abilities': 'Yaka arrow control, Leadership, Space survival, Hunting skills'}),
    
    # === Supporting Characters ===
    ('c950', 'Character', {'name': 'Happy Hogan', 'real_name': 'Harold Hogan', 'species': 'Human', 'first_appearance': 'Tales of Suspense #42 (October 1963)', 'abilities': 'Bodyguard training, Driving, Loyal friend'}),
    ('c951', 'Character', {'name': 'Pepper Potts', 'real_name': 'Virginia Potts', 'species': 'Human', 'first_appearance': 'Tales of Suspense #45 (January 1964)', 'abilities': 'Business acumen, Management, Intelligence, Stark Industries leadership'}),
    ('c952', 'Character', {'name': 'War Machine (James Rhodes)', 'real_name': 'James Rhodes', 'species': 'Human', 'first_appearance': 'Iron Man #118 (January 1979)', 'abilities': 'Powered armor, Flight, Weapon systems', 'note': 'duplicate_check'}),
    ('c953', 'Character', {'name': 'Ant-Man (Scott Lang)', 'real_name': 'Scott Lang', 'species': 'Human', 'first_appearance': 'Avengers #181 (March 1979)', 'abilities': 'Size manipulation, Insect communication', 'note': 'duplicate_check'}),
    ('c954', 'Character', {'name': 'Wasp (Hope Van Dyne)', 'real_name': 'Hope Van Dyne', 'species': 'Human (Enhanced)', 'first_appearance': 'Tales of Suspense #44 (December 1963)', 'abilities': 'Size manipulation, Bio-electric blasts, Flight, Martial arts'}),
    ('c955', 'Character', {'name': 'Ant-Man (Hank Pym)', 'real_name': 'Henry Pym', 'species': 'Human (Enhanced)', 'first_appearance': 'Tales to Astonish #27 (January 1962)', 'abilities': 'Size manipulation, Pym particles, Genius intellect, Insect control'}),
    
    # === More X-Men variants ===
    ('c960', 'Character', {'name': 'Kitty Pryde', 'real_name': 'Katherine Pryde', 'species': 'Mutant', 'first_appearance': 'Uncanny X-Men #129 (January 1980)', 'abilities': 'Phasing, Intangibility, Stealth, Computer hacking'}),
    ('c961', 'Character', {'name': 'Mystique', 'real_name': 'Raven Darkholme', 'species': 'Mutant', 'first_appearance': 'Ms. Marvel #16 (April 1978)', 'abilities': 'Shapeshifting, Slow aging, Enhanced agility, Espionage'}),
    ('c962', 'Character', {'name': 'Sentry', 'real_name': 'Robert Reynolds', 'species': 'Human (Enhanced)', 'first_appearance': 'The Sentry #0 (August 2000)', 'abilities': 'One million exploding suns power, Flight, Invulnerability, Molecular reconstruction'}),
    ('c963', 'Character', {'name': 'Thunderbolt', 'real_name': 'James Rhodes', 'species': 'Human', 'first_appearance': 'Iron Man #118 (January 1979)', 'abilities': 'Military training, Leadership', 'note': 'duplicate_check'}),
    
    # === Additional Heroes ===
    ('c970', 'Character', {'name': 'Ms. Marvel (Kamala Khan)', 'real_name': 'Kamala Khan', 'species': 'Human (Enhanced)', 'first_appearance': 'Captain Marvel #14 (August 2013)', 'abilities': 'Polymorph, Size manipulation, Regeneration, Heroic determination'}),
    ('c971', 'Character', {'name': 'Ironheart', 'real_name': 'Riri Williams', 'species': 'Human', 'first_appearance': 'Invincible Iron Man #1 (November 2008)', 'abilities': 'Genius intellect, Powered armor, Engineering, Scientific innovation'}),
    ('c972', 'Character', {'name': 'She-Hulk', 'real_name': 'Jennifer Walters', 'species': 'Human (Gamma Mutate)', 'first_appearance': 'Savage She-Hulk #1 (February 1980)', 'abilities': 'Superhuman strength, Durability, Lawyer mind, Retains intelligence while transformed'}),
    ('c973', 'Character', {'name': 'Nighthawk', 'real_name': 'Dane Whitman', 'species': 'Human (Enhanced)', 'first_appearance': 'Avengers #71 (July 1969)', 'abilities': 'Enchantress sword, Martial arts, Invisibility cloak, Genius intellect'}),
    
    # === More Villains ===
    ('c980', 'Character', {'name': 'Absorbing Man', 'real_name': 'Carl Creel', 'species': 'Human (Enhanced)', 'first_appearance': 'Journey into Mystery #102 (May 1964)', 'abilities': 'Matter absorption, Power replication, Invulnerability, Shapeshifting'}),
    ('c981', 'Character', {'name': 'Crimson Cowl', 'real_name': 'Unknown', 'species': 'Human', 'first_appearance': 'Unknown', 'abilities': 'Unknown'}),
    ('c982', 'Character', {'name': 'Taskmaster', 'real_name': 'Tony Masters', 'species': 'Human (Enhanced)', 'first_appearance': 'Avengers Annual #7 (1978)', 'abilities': 'Photographic reflexes, Combat mimicry, Master of all fighting styles'}),
    ('c983', 'Character', {'name': 'Crossbones', 'real_name': 'Brock Rumlow', 'species': 'Human (Enhanced)', 'first_appearance': 'Captain America #359 (March 1989)', 'abilities': 'Peak human strength, Combat training, Shield techniques, Assassination'}),
]

NEW_RELS = [
    # Guardians of the Galaxy relationships
    ('c400', 'MEMBER_OF', 't7'), ('c401', 'MEMBER_OF', 't7'), ('c402', 'MEMBER_OF', 't7'),
    ('c403', 'MEMBER_OF', 't7'), ('c404', 'MEMBER_OF', 't7'), ('c405', 'MEMBER_OF', 't7'),
    ('c406', 'MEMBER_OF', 't7'), ('c400', 'ALLY_OF', 'c401'), ('c403', 'ALLY_OF', 'c404'),
    ('c406', 'ENEMY_OF', 'c300'), ('c402', 'ENEMY_OF', 'c300'),
    
    # Fantastic Four relationships
    ('c500', 'MEMBER_OF', 't8'), ('c501', 'MEMBER_OF', 't8'), ('c502', 'MEMBER_OF', 't8'),
    ('c503', 'MEMBER_OF', 't8'), ('c501', 'RELATIVE_OF', 'c502'), ('c500', 'RELATIVE_OF', 'c501'),
    ('c500', 'FROM', 'l19'), ('c501', 'FROM', 'l19'),
    
    # Spider-Man relationships
    ('c100', 'FROM', 'l2'), ('c600', 'RELATIVE_OF', 'c100'), ('c601', 'ENEMY_OF', 'c100'),
    ('c602', 'ENEMY_OF', 'c100'), ('c603', 'ENEMY_OF', 'c100'), ('c604', 'ENEMY_OF', 'c100'),
    ('c605', 'ENEMY_OF', 'c100'), ('c606', 'ENEMY_OF', 'c100'), ('c607', 'ENEMY_OF', 'c100'),
    ('c608', 'ENEMY_OF', 'c609'), ('c609', 'MEMBER_OF', 't9'), ('c610', 'ALLY_OF', 'c609'),
    
    # X-Men relationships
    ('c700', 'MEMBER_OF', 't5'), ('c701', 'MEMBER_OF', 't5'), ('c702', 'MEMBER_OF', 't5'),
    ('c703', 'MEMBER_OF', 't5'), ('c704', 'MEMBER_OF', 't5'), ('c705', 'MEMBER_OF', 't5'),
    ('c707', 'MEMBER_OF', 't6'), ('c708', 'ENEMY_OF', 'c200'), ('c708', 'ENEMY_OF', 'c202'),
    ('c709', 'ENEMY_OF', 't5'), ('c709', 'ENEMY_OF', 'c200'),
    ('c205', 'ENEMY_OF', 'c700'), ('c202', 'ALLY_OF', 'c700'), ('c203', 'ALLY_OF', 'c700'),
    
    # Avengers relationships
    ('c800', 'MEMBER_OF', 't1'), ('c800', 'RELATIVE_OF', 'c2'), ('c802', 'RELATIVE_OF', 'c801'),
    ('c803', 'ALLY_OF', 't1'), ('c804', 'ALLY_OF', 't1'), ('c805', 'ALLY_OF', 't1'),
    ('c806', 'ALLY_OF', 't1'), ('c801', 'MEMBER_OF', 't1'), ('c802', 'MEMBER_OF', 't1'),
    
    # Cosmic relationships
    ('c901', 'HERALD_OF', 'c902'), ('c900', 'ENEMY_OF', 'c300'),
    
    # Heroes for Hire relationships
    ('c910', 'MEMBER_OF', 't10'), ('c911', 'MEMBER_OF', 't10'), ('c910', 'ALLY_OF', 'c100'),
    ('c912', 'MEMBER_OF', 't10'), ('c913', 'MEMBER_OF', 't10'), ('c914', 'MEMBER_OF', 't1'),
    ('c915', 'MEMBER_OF', 't1'), ('c914', 'FROM', 'l10'), ('c915', 'FROM', 'l10'),
    ('c914', 'RELATIVE_OF', 'c102'),
    
    # Young Avengers
    ('c930', 'MEMBER_OF', 't11'), ('c931', 'MEMBER_OF', 't11'), ('c932', 'MEMBER_OF', 't11'),
    ('c933', 'MEMBER_OF', 't11'), ('c930', 'ALLY_OF', 'c6'),
    
    # More villain relationships
    ('c921', 'ENEMY_OF', 'c100'), ('c922', 'ENEMY_OF', 'c100'), ('c923', 'ENEMY_OF', 'c2'),
    ('c923', 'ENEMY_OF', 't1'), ('c980', 'ENEMY_OF', 'c3'), ('c982', 'ENEMY_OF', 't1'),
    
    # Support characters
    ('c950', 'MEMBER_OF', 't3'), ('c951', 'MEMBER_OF', 't3'), ('c951', 'ALLY_OF', 'c1'),
    ('c954', 'RELATIVE_OF', 'c955'), ('c955', 'MEMBER_OF', 't1'), ('c954', 'MEMBER_OF', 't1'),
    ('c970', 'MEMBER_OF', 't1'), ('c971', 'MEMBER_OF', 't1'),
    ('c972', 'MEMBER_OF', 't1'), ('c973', 'MEMBER_OF', 't1'),
]

NEW_TEAMS = [
    ('t7', 'Team', {'name': 'Guardians of the Galaxy', 'type': 'Space Team'}),
    ('t8', 'Team', {'name': 'Fantastic Four', 'type': 'Superhero Team'}),
    ('t9', 'Team', {'name': 'Defenders', 'type': 'Superhero Team'}),
    ('t10', 'Team', {'name': 'Heroes for Hire', 'type': 'Mercenary Team'}),
    ('t11', 'Team', {'name': 'Young Avengers', 'type': 'Young Hero Team'}),
    ('t12', 'Team', {'name': 'Secret Avengers', 'type': 'Covert Team'}),
    ('t13', 'Team', {'name': 'West Coast Avengers', 'type': 'Regional Team'}),
    ('t14', 'Team', {'name': 'A-Force', 'type': 'All-Female Team'}),
    ('t15', 'Team', {'name': 'New Avengers', 'type': 'Superhero Team'}),
    ('t16', 'Team', {'name': 'Savage Avengers', 'type': 'Primal Team'}),
]

NEW_LOCATIONS = [
    ('l20', 'Location', {'name': 'New Atlantis', 'type': 'City'}),
    ('l21', 'Location', {'name': 'Hell\'s Kitchen', 'type': 'Neighborhood'}),
    ('l22', 'Location', {'name': 'Sanctum Sanctorum', 'type': 'Mystical Building'}),
    ('l23', 'Location', {'name': 'Xavier School', 'type': 'School'}),
    ('l24', 'Location', {'name': 'Baxter Building', 'type': 'Headquarters'}),
    ('l25', 'Location', {'name': 'Ravencroft Institute', 'type': 'Asylum'}),
    ('l26', 'Location', {'name': 'Osborn Tower', 'type': 'Headquarters'}),
    ('l27', 'Location', {'name': 'Madripoor', 'type': 'Island Nation'}),
    ('l28', 'Location', {'name': 'Sokovia', 'type': 'Nation'}),
    ('l29', 'Location', {'name': 'Wundagore Mountain', 'type': 'Mountain'}),
    ('l30', 'Location', {'name': 'Kamar-Taj', 'type': 'Mystical School'}),
    ('l31', 'Location', {'name': 'Prison Raft', 'type': 'Prison'}),
    ('l32', 'Location', {'name': 'The Vault', 'type': 'Prison'}),
    ('l33', 'Location', {'name': 'Sanctum', 'type': 'Mystical Building'}),
]

NEW_MOVIES = [
    ('m10', 'Movie', {'title': 'Spider-Man', 'year': '2002'}),
    ('m11', 'Movie', {'title': 'X-Men', 'year': '2000'}),
    ('m12', 'Movie', {'title': 'Blade', 'year': '1998'}),
    ('m13', 'Movie', {'title': 'Daredevil', 'year': '2003'}),
    ('m14', 'Movie', {'title': 'Fantastic Four', 'year': '2005'}),
    ('m15', 'Movie', {'title': 'Iron Man 2', 'year': '2010'}),
    ('m16', 'Movie', {'title': 'Thor', 'year': '2011'}),
    ('m17', 'Movie', {'title': 'Captain America: The First Avenger', 'year': '2011'}),
    ('m18', 'Movie', {'title': 'The Incredible Hulk', 'year': '2008'}),
    ('m19', 'Movie', {'title': 'Iron Man 3', 'year': '2013'}),
    ('m20', 'Movie', {'title': 'Captain America: The Winter Soldier', 'year': '2014'}),
    ('m21', 'Movie', {'title': 'Ant-Man', 'year': '2015'}),
    ('m22', 'Movie', {'title': 'Doctor Strange', 'year': '2016'}),
    ('m23', 'Movie', {'title': 'Guardians of the Galaxy Vol. 2', 'year': '2017'}),
    ('m24', 'Movie', {'title': 'Thor: Ragnarok', 'year': '2017'}),
    ('m25', 'Movie', {'title': 'Ant-Man and the Wasp', 'year': '2018'}),
    ('m26', 'Movie', {'title': 'Captain Marvel', 'year': '2019'}),
    ('m27', 'Movie', {'title': 'Shang-Chi and the Legend of the Ten Rings', 'year': '2021'}),
    ('m28', 'Movie', {'title': 'Eternals', 'year': '2021'}),
    ('m29', 'Movie', {'title': 'Spider-Man: Far From Home', 'year': '2019'}),
]

NEW_EVENTS = [
    ('e10', 'Event', {'event_name': 'Secret Invasion', 'year': '2008'}),
    ('e11', 'Event', {'event_name': 'Civil War II', 'year': '2016'}),
    ('e12', 'Event', {'event_name': 'Age of Apocalypse', 'year': '1995'}),
    ('e13', 'Event', {'event_name': 'House of M', 'year': '2005'}),
    ('e14', 'Event', {'event_name': 'Dark Phoenix Saga', 'year': '1980'}),
    ('e15', 'Event', {'event_name': 'Krakoa Era', 'year': '2019'}),
    ('e16', 'Event', {'event_name': 'Original Sin', 'year': '2014'}),
    ('e17', 'Event', {'event_name': 'Infinity Gauntlet', 'year': '1991'}),
    ('e18', 'Event', {'event_name': 'Onslaught Saga', 'year': '1996'}),
    ('e19', 'Event', {'event_name': 'Days of Future Past', 'year': '1981'}),
    ('e20', 'Event', {'event_name': 'Secret Wars (2015)', 'year': '2015'}),
]

NEW_ITEMS = [
    ('i200', 'Item', {'item_name': 'Web Shooters', 'type': 'Equipment'}),
    ('i201', 'Item', {'item_name': 'Hulkbuster Armor', 'type': 'Powered Armor'}),
    ('i202', 'Item', {'item_name': 'Ten Rings', 'type': 'Mystical Artifact'}),
    ('i203', 'Item', {'item_name': 'Cloak of Levitation', 'type': 'Mystical Artifact'}),
    ('i204', 'Item', {'item_name': 'Wakandan Kimoyo Beads', 'type': 'Technology'}),
    ('i205', 'Item', {'item_name': 'Pym Particles', 'type': 'Scientific Discovery'}),
    ('i206', 'Item', {'item_name': 'Vibranium', 'type': 'Metal'}),
    ('i207', 'Item', {'item_name': 'Adamantium', 'type': 'Metal'}),
    ('i208', 'Item', {'item_name': 'Aether', 'type': 'Infinity Stone Container'}),
    ('i209', 'Item', {'item_name': 'Tesseract', 'type': 'Space Stone Container'}),
    ('i210', 'Item', {'item_name': 'Loki\'s Scepter', 'type': 'Weapon'}),
    ('i211', 'Item', {'item_name': 'Eye of Agamotto', 'type': 'Mystical Artifact'}),
    ('i212', 'Item', {'item_name': 'Cosmic Cube', 'type': 'Infinity Artifact'}),
    ('i213', 'Item', {'item_name': 'Infinity Formula', 'type': 'Chemical'}),
    ('i214', 'Item', {'item_name': 'Heart-Shaped Herb', 'type': 'Plant'}),
]

def main():
    existing_entities = get_existing_entities()
    print(f"Existing entities: {len(existing_entities)}")
    
    all_new = []
    total_new = 0
    
    # Add nodes
    for item in NEW_CHARS:
        var, label, props = item
        if 'note' in props and props['note'] == 'duplicate_check':
            # Check if this is a dup
            entity_key = f"{label}:{props.get('name', '')}"
            if entity_key in existing_entities:
                print(f"  SKIP duplicate: {entity_key}")
                continue
        entity_key = f"{label}:{props.get('name', '')}"
        if entity_key in existing_entities:
            print(f"  SKIP duplicate: {entity_key}")
            continue
        stmt = build_node(var, label, props)
        if stmt:
            all_new.append(stmt)
            existing_entities.add(entity_key)
            total_new += 1
    
    # Add teams
    for item in NEW_TEAMS:
        var, label, props = item
        entity_key = f"{label}:{props.get('name', '')}"
        if entity_key in existing_entities:
            print(f"  SKIP duplicate team: {entity_key}")
            continue
        stmt = build_node(var, label, props)
        if stmt:
            all_new.append(stmt)
            existing_entities.add(entity_key)
            total_new += 1
    
    # Add locations
    for item in NEW_LOCATIONS:
        var, label, props = item
        entity_key = f"{label}:{props.get('name', '')}"
        if entity_key in existing_entities:
            print(f"  SKIP duplicate location: {entity_key}")
            continue
        stmt = build_node(var, label, props)
        if stmt:
            all_new.append(stmt)
            existing_entities.add(entity_key)
            total_new += 1
    
    # Add movies
    for item in NEW_MOVIES:
        var, label, props = item
        entity_key = f"{label}:{props.get('title', '')}"
        if entity_key in existing_entities:
            print(f"  SKIP duplicate movie: {entity_key}")
            continue
        stmt = build_node(var, label, props, name_key='title')
        if stmt:
            all_new.append(stmt)
            existing_entities.add(entity_key)
            total_new += 1
    
    # Add events
    for item in NEW_EVENTS:
        var, label, props = item
        entity_key = f"{label}:{props.get('event_name', '')}"
        if entity_key in existing_entities:
            print(f"  SKIP duplicate event: {entity_key}")
            continue
        stmt = build_node(var, label, props, name_key='event_name')
        if stmt:
            all_new.append(stmt)
            existing_entities.add(entity_key)
            total_new += 1
    
    # Add items
    for item in NEW_ITEMS:
        var, label, props = item
        entity_key = f"{label}:{props.get('item_name', '')}"
        if entity_key in existing_entities:
            print(f"  SKIP duplicate item: {entity_key}")
            continue
        stmt = build_node(var, label, props, name_key='item_name')
        if stmt:
            all_new.append(stmt)
            existing_entities.add(entity_key)
            total_new += 1
    
    # Add relationships
    for item in NEW_RELS:
        var, rel_type, target = item
        stmt = f"MERGE ({var})-[:{rel_type}]->({target});"
        all_new.append(stmt)
        total_new += 1
    
    # Write
    with open(CYPER_FILE, 'a') as f:
        for stmt in all_new:
            f.write(stmt + '\n')
    
    print(f"\nAdded {total_new} new statements")
    
    # Count
    with open(CYPER_FILE, 'r') as f:
        lines = f.readlines()
        total_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    print(f"Total Cypher lines: {total_lines}")
    
    # Validation
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    errors = []
    for i, line in enumerate(content.strip().split('\n'), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if not line.startswith('MERGE'):
            errors.append(f"Line {i}: Not MERGE")
    if errors:
        print(f"Validation errors: {len(errors)}")
    else:
        print("Validation: OK")
    
    # Telemetry
    try:
        with open(TELEMETRY_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                'EXPANSION_BATCH',
                '5',
                str(total_new),
                str(total_new),
                str(total_lines),
                'success'
            ])
        print("Telemetry logged")
    except:
        print("Telemetry logging skipped")
    
    print("\nTASK_BATCH_COMPLETED")

if __name__ == '__main__':
    main()
