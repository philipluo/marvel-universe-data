#!/usr/bin/env python3
"""Add Chinese names (name_cn) to all Character nodes in the Cypher file."""
import re
import os

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')

# English -> Chinese name mapping
CN_MAP = {
    # === Core Avengers ===
    'Iron Man': '钢铁侠',
    'Captain America': '美国队长',
    'Thor': '雷神',
    'Hulk': '浩克',
    'Black Widow': '黑寡妇',
    'Hawkeye': '鹰眼',
    'Nick Fury': '尼克·弗瑞',
    
    # === More Avengers ===
    'Spider-Man': '蜘蛛侠',
    'Doctor Strange': '奇异博士',
    "Black Panther": '黑豹',
    'Captain Marvel': '惊奇队长',
    'Ant-Man': '蚁人',
    'Scarlet Witch': '绯红女巫',
    'Falcon': '猎鹰',
    'War Machine': '战争机器',
    'Winter Soldier': '冬日战士',
    'Quicksilver': '快银',
    'Hercules': '赫拉克勒斯',
    'Shang-Chi': '尚气',
    'Blade': '刀锋战士',
    'Ghost Rider': '恶灵骑士',
    'She-Hulk': '女浩克',
    "Ms. Marvel (Kamala Khan)": '惊奇女士',
    'Ironheart': '钢铁之心',
    'Wasp (Hope Van Dyne)': '黄蜂女',
    'Ant-Man (Scott Lang)': '蚁人(斯科特·朗)',
    'Ant-Man (Hank Pym)': '蚁人(汉克·皮姆)',
    'Hank Pym': '汉克·皮姆',
    'Wasp (Hope Van Dyne)': '黄蜂女(霍普·范·戴恩)',
    'Invisible Woman': '隐形女',
    'Sue Storm': '苏·斯托姆',
    'Kingpin': '金并',
    'Wilson Fisk': '威尔逊·菲斯克',
    'Thunderbolt': '雷鸣',
    
    # === X-Men ===
    'Professor X': 'X教授',
    'Cyclops': '镭射眼',
    'Wolverine': '金刚狼',
    'Storm': '暴风女',
    'Jean Grey': '琴·葛雷',
    'Magneto': '万磁王',
    'Beast': '野兽',
    'Iceman': '冰人',
    'Angel': '天使',
    'Rogue': '罗根',
    'Gambit': '牌皇',
    'Colossus': '钢力士',
    'Nightcrawler': '夜行者',
    'Psylocke': '灵蝶',
    'Cable': ' Cable',
    'Emma Frost': '白皇后',
    'Sabretooth': '剑齿虎',
    'Apocalypse': '天启',
    'Mystique': '魔形女',
    'Kitty Pryde': '浦瑞德',
    'Sentry': '信使',
    'Cable': ' Cable',
    'Nathan Summers': '内森·萨默斯',
    'Warpath': '战争之路',
    'Remy LeBeau': '雷米·勒博',
    'Anna Marie': '安娜·玛丽',
    'Piotr Rasputin': '彼得·拉斯普廷',
    'Kurt Wagner': '库尔特·瓦格纳',
    'Betsy Braddock': '贝丝·布拉多克',
    'Victor Creed': '维克多·克里德',
    'En Sabah Nur': '恩·沙巴·努尔',
    'Raven Darkholme': '瑞雯·达克霍姆',
    'Katherine Pryde': '凯瑟琳·浦瑞德',
    'Robert Reynolds': '罗伯特·雷诺兹',
    
    # === Guardians ===
    'Star-Lord': '星爵',
    'Gamora': '卡魔拉',
    'Drax': '毁灭者德拉克斯',
    'Rocket Raccoon': '火箭浣熊',
    'Groot': '格鲁特',
    'Mantis': '螳螂女',
    'Nebula': '星云',
    'Yondu': '勇度',
    'Ronan': '罗南',
    'Thanos': '灭霸',
    'Loki': '洛基',
    'Mary Jane Watson': '玛丽·简·沃森',
    'J. Jonah Jameson': 'J·乔纳·詹姆森',
    'Ned Leeds': '内德·利兹',
    'Nighthawk': '夜枭',
    'Crimson Cowl': '深红兜帽',
    'Heralds of Galactus': '行星吞噬者使者',
    'War Machine (James Rhodes)': '战争机器(詹姆斯·罗德斯)',
    'Peter Quill': '彼得·奎尔',
    'Peter Quill': '彼得·奎尔',
    
    # === Fantastic Four ===
    'Mister Fantastic': '神奇先生',
    'Invisible Woman': '隐形女',
    'Human Torch': '霹雳火',
    'The Thing': '石头人',
    'Reed Richards': '里德·理查兹',
    'Susan Storm': '苏珊·斯托姆',
    'Johnny Storm': '约翰尼·斯托姆',
    'Ben Grimm': '本·格里姆',
    
    # === Villains ===
    'Doctor Doom': '毁灭博士',
    'Green Goblin': '绿妖',
    'Red Skull': '红骷髅',
    'Ultron': '奥创',
    'Venom': '毒液',
    'Green Goblin': '绿妖',
    'Norman Osborn': '诺曼·奥斯本',
    'Johann Schmidt': '约翰·施密特',
    'Eddie Brock': '埃迪·布洛克',
    'Carnage': '屠杀',
    'Cletus Kasady': '克莱图斯·卡萨迪',
    'Mysterio': '神秘客',
    'Mandarin': '满大人',
    'Absorbing Man': '吸收人',
    'Carl Creel': '卡尔·克雷尔',
    'Taskmaster': '任务大师',
    'Tony Masters': '托尼·马斯特斯',
    'Crossbones': '交叉骨',
    'Brock Rumlow': '布罗克·朗姆洛',
    'Doc Ock': '章鱼博士',
    'Otto Octavius': '奥托·奥克塔维厄斯',
    'Sandman': '沙人',
    'Flint Marko': '弗林特·马尔科',
    'Electro': '电光人',
    'Max Dillon': '麦克斯·戴伦',
    'Lizard': '蜥蜴人',
    'Curt Connors': '柯特·康纳斯',
    'Vulture': '秃鹫',
    'Adrian Toomes': '阿德里安·图姆斯',
    
    # === Street Heroes ===
    'Daredevil': '夜魔侠',
    'Elektra': '艾蕾克特拉',
    'Punisher': '惩罚者',
    'Luke Cage': '卢克·凯奇',
    'Iron Fist': '铁拳',
    'Jessica Jones': '杰西卡·琼斯',
    'Moon Knight': '月光骑士',
    'Matt Murdock': '马特·默多克',
    'Elektra Natchios': '艾蕾克特拉·纳奇奥斯',
    'Frank Castle': '弗兰克·卡塞尔',
    'Carl Lucas': '卡尔·卢卡斯',
    'Danny Rand': '丹尼·兰德',
    'Jessica Campbell Jones': '杰西卡·坎贝尔·琼斯',
    'Marc Spector': '马克·斯皮克特',
    
    # === Cosmic ===
    'Silver Surfer': '银影侠',
    'Galactus': '行星吞噬者',
    'Captain Universe': '宇宙队长',
    'Norrin Radd': '诺林·拉德',
    'Galan': '伽兰',
    
    # === Young Avengers ===
    'Hawkeye (Kate Bishop)': '鹰眼(凯特·毕肖普)',
    'Wiccan': '巫术',
    'Speed': '速度',
    'Stature': '巨化女',
    'Kate Bishop': '凯特·毕肖普',
    'William Kaplan': '威廉·卡普兰',
    'Thomas Maximoff': '托马斯·马克西莫夫',
    'Cassie Lang': '卡西·朗',
    
    # === Supporting ===
    'Happy Hogan': '快乐·霍根',
    'Pepper Potts': '佩珀·波茨',
    'Shuri': '舒莉',
    'Okoye': '奥科耶',
    'Hope Van Dyne': '霍普·范·戴恩',
    'Riri Williams': '里里·威廉姆斯',
    'Jennifer Walters': '詹妮弗·沃尔特斯',
    'Dane Whitman': '戴恩·惠特曼',
    'Kamala Khan': '卡玛拉·汗',
    
    # === Movies (titles also need Chinese for display) ===
    'Iron Man': '钢铁侠',
    'The Avengers': '复仇者联盟',
    'Guardians of the Galaxy': '银河护卫队',
    'Doctor Strange': '奇异博士',
    'Black Panther': '黑豹',
    'Avengers: Infinity War': '复仇者联盟：无限战争',
    'Avengers: Endgame': '复仇者联盟：终局之战',
    'Spider-Man: No Way Home': '蜘蛛侠：英雄无归',
}

def add_chinese_names():
    with open(CYPER_FILE, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    changed = 0
    
    for line in lines:
        stripped = line.strip()
        # Only process Character nodes
        if not stripped.startswith('MERGE') or ':Character' not in stripped:
            new_lines.append(line)
            continue
        
        # Check if name_cn already exists
        if 'name_cn' in stripped:
            new_lines.append(line)
            continue
        
        # Find the character name
        match = re.search(r'name:\s*"([^"]+)"', stripped)
        if not match:
            new_lines.append(line)
            continue
        
        eng_name = match.group(1)
        cn_name = CN_MAP.get(eng_name)
        
        if cn_name:
            # Insert name_cn right after name
            new_line = stripped.replace(
                f'name: "{eng_name}"',
                f'name: "{eng_name}", name_cn: "{cn_name}"'
            ) + '\n'
            new_lines.append(new_line)
            changed += 1
        else:
            print(f"  WARNING: No Chinese name for: {eng_name}")
            new_lines.append(line)
    
    # Write back
    with open(CYPER_FILE, 'w') as f:
        f.writelines(new_lines)
    
    print(f"\nDone! Added name_cn to {changed} character nodes")
    print(f"Total lines: {len(new_lines)}")
    
    # Verify
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    with_cn = len(re.findall(r'name_cn:', content))
    print(f"Nodes with name_cn: {with_cn}")
    
    # Sample output
    print("\nSample:")
    for line in new_lines:
        if 'name_cn' in line and ':Character' in line:
            print(line.strip()[:120] + '...')
            break

if __name__ == '__main__':
    add_chinese_names()
