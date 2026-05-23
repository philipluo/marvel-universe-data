#!/usr/bin/env python3
"""Translate all Marvel fields to Chinese."""
import re
import os

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')

# === ABILITIES TRANSLATION ===
ABILITIES_MAP = {
    'Genius-level intellect': '天才级智力',
    'Powered armor suit': '动力装甲',
    'Flight': '飞行',
    'Repulsor rays': '冲击射线',
    'Superhuman strength via armor': '装甲强化力量',
    'Superhuman strength': '超人类力量',
    'agility': '敏捷',
    'speed': '速度',
    'endurance': '耐力',
    'Master tactician': '大师级战术家',
    'Vibranium shield expert': '振金盾牌专家',
    'Weather control': '天气控制',
    'Lightning manipulation': '雷电操控',
    'Flight via Mjolnir': '妙尔尼尔飞行',
    'Extended lifespan': '延长寿命',
    'Unlimited strength': '无限力量',
    'Regenerative healing factor': '再生治愈因子',
    'Superhuman durability': '超人类耐力',
    'Genius intelligence': '天才智力',
    'Master spy': '大师级间谍',
    'Expert martial artist': '武术专家',
    'Slowed aging': '延缓衰老',
    'Weapons expert': '武器专家',
    'Red Room training': '红房训练',
    'Master archer': '大师级弓箭手',
    'Expert marksman': '神枪手',
    'Hand-to-hand combat': '徒手格斗',
    'Trick arrows': '特制箭矢',
    'Master strategist': '大师级战略家',
    'Expert combatant': '战斗专家',
    'Espionage master': '间谍大师',
    'Leadership': '领导力',
    'Wall-crawling': '壁虎攀爬',
    'Spider-sense': '蜘蛛感应',
    'Web-slinging': '摆荡',
    'Master of mystic arts': '秘术大师',
    'Time manipulation': '时间操控',
    'Astral projection': '灵体投射',
    'Teleportation': '传送',
    'Superhuman strength via Heart-Shaped Herb': '心形草强化力量',
    'Vibranium suit': '振金战衣',
    'Master combatant': '战斗大师',
    'Human/Kree Hybrid': '人类/克里混血',
    'Energy projection': '能量投射',
    'Photon blasts': '光子冲击',
    'Cosmic awareness': '宇宙感知',
    'Size manipulation': '大小操控',
    'Insect communication': '昆虫沟通',
    'Superhuman strength when small': '缩小时超力量',
    'Reality warping': '现实扭曲',
    'Chaos magic': '混沌魔法',
    'Telekinesis': '念力',
    'Mind manipulation': '心灵操控',
    'Flight via mechanical wings': '机械翼飞行',
    'Telepathic link with birds': '鸟类心灵链接',
    'Various weapons systems': '多种武器系统',
    'Telepathy': '心灵感应',
    'Mind control': '心灵控制',
    'Mental projection': '精神投射',
    'Optic blasts': '光学冲击',
    'Expert tactician': '战术专家',
    'Adamantium claws': '艾德曼合金爪',
    'Superhuman senses': '超人类感官',
    'Enhanced strength': '强化力量',
    'Healing factor': '治愈因子',
    'Cryokinesis': '冷冻能力',
    'Ice form transformation': '冰形态变换',
    'Temperature reduction': '降温',
    'Winged flight': '翼飞行',
    'Feather projection': '羽毛投射',
    'Eternal (Deviant)': '永恒族（变异者）',
    'Superhuman strength, Durability': '超人类力量与耐力',
    'Frost Giant': '霜巨人',
    'Magic': '魔法',
    'Shapeshifting': '变形',
    'Illusion casting': '幻术',
    'Sorcery': '巫术',
    'Powered armor': '动力装甲',
    'Diplomatic immunity': '外交豁免权',
    'Goblin formula effects': '绿妖公式效果',
    'Advanced gadgets': '先进装备',
    'Strategic genius': '战略天才',
    'Cosmo radiation enhanced physiology': '宇宙射线强化体质',
    'Artificial Intelligence': '人工智能',
    'Symbiote Host': '共生体宿主',
    'Camouflage': '伪装',
    'Spider-sense disruption': '蜘蛛感应干扰',
    'Human': '人类',
    'Human (Enhanced)': '人类（强化）',
    'Human (Gamma Mutate)': '人类（伽马突变）',
    'Mutant': '变种人',
    'Mutant (Enhanced)': '变种人（强化）',
    'Asgardian': '阿斯加德人',
    'Mutant (Cyborg)': '变种人（改造）',
    'Human/Celestial Hybrid': '人类/天神族混血',
    'Zen-Whoberian': ' zen-Whoberian',
    'Genetically Engineered Raccoon': '基因改造浣熊',
    'Flora Colossus': '植物巨人',
    'Human (Enhanced)': '人类（强化）',
    'Luphomoid': '卢福莫伊人',
    'Human (Rock-like)': '人类（岩石形态）',
    'Human (Silicate)': '人类（硅基）',
    'Human/Reptile Hybrid': '人类/爬行动物混血',
    'Vampire-Human Hybrid': '吸血鬼-人类混血',
    'Human (Demon Bond)': '人类（恶魔契约）',
    'Various': '多种',
    'Human (Enhanced)': '人类（强化）',
    'Olympian God': '奥林匹斯神',
    'Cosmic Entity Host': '宇宙实体宿主',
    'Human/Cosmic Entity': '人类/宇宙实体',
    'Cosmic Entity': '宇宙实体',
    'Centaurian': '半人马座人',
    'Human (Rock-like)': '人类（岩石形态）',
    'Mutant (Deviant)': '变种人（变异者）',
    'Human/Celestial': '人类/天神族',
    'Symbiote Host': '共生体宿主',
    'Human (Enhanced)': '人类（强化）',
    'Human (Rock-like)': '人类（岩石形态）',
    'Human (Gamma Mutate)': '人类（伽马突变）',
    'Mutant': '变种人',
    'Olympian God': '奥林匹斯神',
    'Human': '人类',
    'Vampire-Human Hybrid': '吸血鬼-人类混血',
    'Human (Demon Bond)': '人类（恶魔契约）',
    'Human (Enhanced)': '人类（强化）',
    'Human': '人类',
    'Human (Enhanced)': '人类（强化）',
    'Various': '多种',
    'Human (Deviant)': '人类（变异者）',
    'Human': '人类',
    'Human (Enhanced)': '人类（强化）',
    'Human (Gamma Mutate)': '人类（伽马突变）',
}

# === SPECIES TRANSLATION (already covered above, consolidate) ===
SPECIES_MAP = {
    'Human': '人类',
    'Human (Enhanced)': '人类（强化）',
    'Human (Gamma Mutate)': '人类（伽马突变）',
    'Mutant': '变种人',
    'Mutant (Enhanced)': '变种人（强化）',
    'Mutant (Cyborg)': '变种人（改造）',
    'Asgardian': '阿斯加德人',
    'Eternal (Deviant)': '永恒族（变异者）',
    'Frost Giant': '霜巨人',
    'Artificial Intelligence': '人工智能',
    'Symbiote Host': '共生体宿主',
    'Human/Celestial Hybrid': '人类/天神族混血',
    'Human/Cosmic Entity': '人类/宇宙实体',
    'Cosmic Entity': '宇宙实体',
    'Olympian God': '奥林匹斯神',
    'Human (Rock-like)': '人类（岩石形态）',
    'Human/Silicate': '人类/硅基',
    'Human/Reptile Hybrid': '人类/爬行动物混血',
    'Vampire-Human Hybrid': '吸血鬼-人类混血',
    'Human (Demon Bond)': '人类（恶魔契约）',
    'Centaurian': '半人马座人',
    'Zen-Whoberian': '泽恩-沃伯里人',
    'Luphomoid': '卢福莫伊人',
    'Genetically Engineered Raccoon': '基因改造浣熊',
    'Flora Colossus': '植物巨人',
}

# === TEAM TYPE TRANSLATION ===
TEAM_TYPE_MAP = {
    'Superhero Team': '超级英雄团队',
    'Intelligence Agency': '情报机构',
    'Technology Company': '科技公司',
    'Space Team': '太空团队',
    'Young Hero Team': '少年英雄团队',
    'Covert Team': '秘密行动团队',
    'Regional Team': '地区团队',
    'All-Female Team': '全女性团队',
    'Primal Team': '原始团队',
}

# === LOCATION TYPE TRANSLATION ===
LOCATION_TYPE_MAP = {
    'Nation': '国家',
    'Island Nation': '岛国',
    'Cosmic Location': '太空地点',
    'Moon': '卫星',
    'School': '学校',
    'Mystical Building': '神秘建筑',
    'Headquarters': '总部',
    'Realm': '维度',
    'City': '城市',
    'Neighborhood': '街区',
    'Asylum': '精神病院',
    'Mountain': '山脉',
    'Mystical School': '神秘学院',
    'Prison': '监狱',
}

# === MOVIE TITLE TRANSLATION ===
MOVIE_TITLE_MAP = {
    'Iron Man': '钢铁侠',
    'The Avengers': '复仇者联盟',
    'Guardians of the Galaxy': '银河护卫队',
    'Doctor Strange': '奇异博士',
    'Black Panther': '黑豹',
    'Avengers: Infinity War': '复仇者联盟：无限战争',
    'Avengers: Endgame': '复仇者联盟：终局之战',
    'Spider-Man: No Way Home': '蜘蛛侠：英雄无归',
    'Spider-Man': '蜘蛛侠',
    'X-Men': 'X战警',
    'Blade': '刀锋战士',
    'Daredevil': '夜魔侠',
    'Fantastic Four': '神奇四侠',
    'Iron Man 2': '钢铁侠2',
    'Thor': '雷神',
    'Captain America: The First Avenger': '美国队长：复仇者先锋',
    'The Incredible Hulk': '无敌浩克',
    'Iron Man 3': '钢铁侠3',
    'Captain America: The Winter Soldier': '美国队长2：冬日战士',
    'Ant-Man': '蚁人',
    'Guardians of the Galaxy Vol. 2': '银河护卫队2',
    'Thor: Ragnarok': '雷神3：诸神黄昏',
    'Ant-Man and the Wasp': '蚁人2：黄蜂女现身',
    'Captain Marvel': '惊奇队长',
    'Shang-Chi and the Legend of the Ten Rings': '尚气与十环传奇',
    'Eternals': '永恒族',
    'Spider-Man: Far From Home': '蜘蛛侠：英雄远征',
}

# === EVENT NAME TRANSLATION ===
EVENT_NAME_MAP = {
    'Battle of New York': '纽约之战',
    'Battle of Sokovia': '索科维亚之战',
    'Infinity War': '无限战争',
    'The Blip': '弹指事件',
    'Civil War': '内战',
    'Secret Wars': '秘密战争',
    'Secret Invasion': '秘密入侵',
    'Civil War II': '内战2',
    'Age of Apocalypse': '天启时代',
    'House of M': 'M王国',
    'Dark Phoenix Saga': '黑凤凰传说',
    'Krakoa Era': '克拉科亚时代',
    'Original Sin': '原罪',
    'Infinity Gauntlet': '无限手套',
    'Onslaught Saga': '买克塔传说',
    'Days of Future Past': '未来昔日',
    'Secret Wars (2015)': '秘密战争（2015）',
}

# === ITEM NAME TRANSLATION ===
ITEM_NAME_MAP = {
    'Space Stone': '空间宝石',
    'Mind Stone': '心灵宝石',
    'Reality Stone': '现实宝石',
    'Power Stone': '力量宝石',
    'Time Stone': '时间宝石',
    'Soul Stone': '灵魂宝石',
    'Infinity Gauntlet': '无限手套',
    'Vibranium Shield': '振金盾牌',
    'Mjolnir': '妙尔尼尔（雷神之锤）',
    'Iron Man Armor': '钢铁侠战甲',
    'Arc Reactor': '弧反应堆',
    "Widow's Bite": '寡妇之吻',
    'Hawkeye Bow': '鹰眼弓',
    'Trick Arrows': '特制箭矢',
    'Web Shooters': '蛛网发射器',
    'Hulkbuster Armor': '反浩克装甲',
    'Ten Rings': '十环',
    'Cloak of Levitation': '漂浮斗篷',
    'Wakandan Kimoyo Beads': '瓦坎达科技珠',
    'Pym Particles': '皮姆粒子',
    'Vibranium': '振金',
    'Adamantium': '艾德曼合金',
    'Aether': '现实之海',
    'Tesseract': '宇宙魔方',
    "Loki's Scepter": '洛基权杖',
    'Eye of Agamotto': '阿戈摩托之眼',
    'Cosmic Cube': '宇宙立方',
    'Infinity Formula': '无限公式',
    'Heart-Shaped Herb': '心形草',
}

# === ITEM TYPE TRANSLATION ===
ITEM_TYPE_MAP = {
    'Infinity Stone': '无限宝石',
    'Artifact': '神器',
    'Weapon/Defense': '武器/防御',
    'Weapon': '武器',
    'Powered Armor': '动力装甲',
    'Power Source': '能源核心',
    'Technology': '科技产品',
    'Mystical Artifact': '神秘神器',
    'Scientific Discovery': '科学发现',
    'Metal': '金属',
    'Chemical': '化学品',
    'Plant': '植物',
    'Equipment': '装备',
}

# === ENEMY OF mapping ===
RELATIONSHIP_LABEL_MAP = {
    'MEMBER_OF': '成员',
    'ENEMY_OF': '敌人',
    'ALLY_OF': '盟友',
    'USES': '使用',
    'FROM': '来自',
    'RELATIVE_OF': '亲属',
    'HERALD_OF': '使者',
}

def translate_line(line):
    """Translate a single Cypher line."""
    stripped = line.strip()
    
    # Translate relationship labels
    for label, cn in RELATIONSHIP_LABEL_MAP.items():
        if f':{label}' in stripped:
            stripped = stripped.replace(f':{label}', f':{cn}')
    
    # Translate character abilities
    if 'Character' in stripped:
        for ability, cn in ABILITIES_MAP.items():
            if ability in stripped:
                stripped = stripped.replace(ability, cn)
    
    # Translate species (only if not already translated)
    if 'Character' in stripped and 'species:' in stripped:
        for species, cn in SPECIES_MAP.items():
            if f'species: "{species}"' in stripped:
                stripped = stripped.replace(f'species: "{species}"', f'species: "{cn}"')
    
    # Translate team names/types
    if 'Team' in stripped:
        for type_name, cn_type in TEAM_TYPE_MAP.items():
            if f'type: "{type_name}"' in stripped:
                stripped = stripped.replace(f'type: "{type_name}"', f'type: "{cn_type}"')
    
    # Translate location names/types
    if 'Location' in stripped:
        for type_name, cn_type in LOCATION_TYPE_MAP.items():
            if f'type: "{type_name}"' in stripped:
                stripped = stripped.replace(f'type: "{type_name}"', f'type: "{cn_type}"')
    
    # Translate movie titles
    if 'Movie' in stripped:
        for title, cn_title in MOVIE_TITLE_MAP.items():
            if f'title: "{title}"' in stripped:
                stripped = stripped.replace(f'title: "{title}"', f'title: "{cn_title}"')
    
    # Translate event names
    if 'Event' in stripped:
        for event, cn_event in EVENT_NAME_MAP.items():
            if f'event_name: "{event}"' in stripped:
                stripped = stripped.replace(f'event_name: "{event}"', f'event_name: "{cn_event}"')
    
    # Translate item names
    if 'Item' in stripped:
        for item, cn_item in ITEM_NAME_MAP.items():
            if f'item_name: "{item}"' in stripped:
                stripped = stripped.replace(f'item_name: "{item}"', f'item_name: "{cn_item}"')
            if f'type: "{item}"' in stripped:
                stripped = stripped.replace(f'type: "{item}"', f'type: "{ITEM_TYPE_MAP.get(item, item)}"')
    
    # Translate item types
    if 'Item' in stripped:
        for itype, cn_itype in ITEM_TYPE_MAP.items():
            if f'type: "{itype}"' in stripped:
                stripped = stripped.replace(f'type: "{itype}"', f'type: "{cn_itype}"')
    
    return stripped + '\n'

def main():
    with open(CYPER_FILE, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    changes = 0
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Skip comments and empty lines
        if not stripped or stripped.startswith('#'):
            new_lines.append(line)
            continue
        
        # Translate
        translated = translate_line(line)
        if translated.strip() != line.strip():
            changes += 1
        new_lines.append(translated)
    
    # Write
    with open(CYPER_FILE, 'w') as f:
        f.writelines(new_lines)
    
    print(f"Translation complete!")
    print(f"Changed {changes} lines")
    print(f"Total lines: {len(new_lines)}")
    
    # Verify samples
    print("\n=== Samples ===")
    for line in new_lines[:5]:
        if 'Character' in line and 'name_cn:' in line:
            print(line.strip()[:120] + '...')
    
    print("\n=== Relationships ===")
    for line in new_lines:
        if ']->' in line and '[' in line and 'MERGE' in line:
            print(line.strip()[:100])
            break
    
    print("\n=== Movies ===")
    for line in new_lines:
        if 'Movie' in line and 'title:' in line:
            print(line.strip()[:100])
            break

if __name__ == '__main__':
    main()
