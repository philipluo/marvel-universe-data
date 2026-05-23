#!/usr/bin/env python3
"""Translate ALL abilities to Chinese."""
import re
import os

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')

# === ABILITIES TRANSLATION DICTIONARY ===
ABILITIES = {
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
    'Genius intellect': '天才智力',
    'Flight': '飞行',
    'Enhanced durability': '强化耐力',
    'Flight': '飞行',
    'Martial arts': '武术',
    'Energy manipulation': '能量操控',
    'Cosmic power': '宇宙之力',
    'Weapon mastery': '武器大师',
    'Peak human conditioning': '人类体能巅峰',
    'Master martial artist': '武术大师',
    'Tactical genius': '战术天才',
    'Scientific innovation': '科学创新',
    'Pym particles': '皮姆粒子',
    'Accelerated healing': '加速愈合',
    'Accuser training': '审判者训练',
    'Acrobatics': '杂技技巧',
    'Acting': '表演',
    'Assassin training': '刺客训练',
    'Assassination': '暗杀',
    'Brawling': '徒手搏斗',
    'Cards': '牌术',
    'Charisma': '魅力',
    'Chi manipulation': '气操控',
    'Chi power': '气之力',
    'Claws': '利爪',
    'Combat expertise': '战斗专长',
    'Combat mimicry': '战斗模仿',
    'Computer hacking': '电脑破解',
    'Crescent weapons': '弯月武器',
    'Criminal mastermind': '犯罪天才',
    'Cybernetic arm': '机械臂',
    'Cybernetic enhancements': '机械增强',
    'Cyborg enhancements': '改造强化',
    'Deception': '欺骗',
    'Detective skills': '侦探技巧',
    'Diamond form': '钻石形态',
    'Driving': '驾驶',
    'Drone control': '无人机操控',
    'Elasticity': '弹性',
    'Electricity generation': '电力生成',
    'Emotion manipulation': '情绪操控',
    'Empathy': '共情',
    'Enchantress sword': '女巫之剑',
    'Energy absorption': '能量吸收',
    'Engineering': '工程学',
    'Enhanced intellect': '强化智力',
    'Enhanced reflexes': '强化反射',
    'Enhanced senses': '强化感官',
    'Espionage': '间谍活动',
    'Expert warrior': '战斗专家',
    'Fencing': '击剑',
    'Fire manipulation': '火焰操控',
    'Fist strike': '铁拳攻击',
    'Force fields': '力场',
    'Godlike strength': '神明之力',
    'Hammer mastery': '锤子大师',
    'Healing': '治愈',
    'Hellfire': '地狱火',
    'Heroic determination': '英雄决心',
    'Hunting skills': '狩猎技巧',
    'Illusion creation': '幻象创造',
    'Immortality': '不死',
    'Immunity to vampire weaknesses': '免疫吸血鬼弱点',
    'Industries leadership': '工业领导',
    'Insect control': '昆虫控制',
    'Intangibility': '虚化',
    'Invisibility': '隐形',
    'Invisibility cloak': '隐形斗篷',
    'Invulnerability': '无敌',
    'Jet boots': '喷射靴',
    'Kinetic energy charging': '动能充能',
    'Lawyer mind': '律师思维',
    'Life force drain': '生命吸取',
    'Loyal friend': '忠诚伙伴',
    'Loyalty': '忠诚',
    'Magnetic force fields': '磁力力场',
    'Management': '管理',
    'Master of all fighting styles': '武术全才',
    'Matter absorption': '物质吸收',
    'Matter manipulation': '物质操控',
    'Mechanical tentacles': '机械触手',
    'Media mogul': '媒体大亨',
    'Mental domination': '精神支配',
    'Milaje leader': '达奥·迈勒领袖',
    'Military training': '军事训练',
    'Molecular manipulation': '分子操控',
    'Molecular reconstruction': '分子重组',
    'Motorcycle transformation': '摩托变形',
    'Multiple personalities': '多重人格',
    'Near': '近',
    'Negate physiology': '生理否定',
    'Ninja training': '忍者训练',
    'One million exploding suns power': '百万太阳爆炸之力',
    'Organic steel transformation': '有机钢变形',
    'Penance stare': '忏悔凝视',
    'Phasing': '相位穿越',
    'Photographic reflexes': '照片反射',
    'Photography': '摄影',
    'Planet devouring': '吞噬星球',
    'Plant control': '植物操控',
    'Political influence': '政治影响力',
    'Polymorph': '变形',
    'Power absorption': '力量吸收',
    'Power replication': '力量复制',
    'Prehensile tail': '卷尾',
    'Prehistoric instincts': '史前本能',
    'Psionic blade': '心灵之刃',
    'Pyrokinesis': '火系能力',
    'Radar sense': '雷达感官',
    'Reflexes': '反射',
    'Regeneration': '再生',
    'Ring mastery': '戒指掌控',
    'Rock': '岩石',
    'Sand form': '沙形',
    'Scavenger technology': '拾荒科技',
    'Scientific genius': '科学天才',
    'Shield techniques': '盾牌技巧',
    'Shrinking': '缩小',
    'Sleep induction': '催眠',
    'Slow aging': '延缓衰老',
    'Social skills': '社交技巧',
    'Solar absorption': '太阳能吸收',
    'Space survival': '太空生存',
    'Spear wielder': '长矛使用',
    'Special effects mastery': '特效大师',
    'Speed force connection': '速度之力连接',
    'Spellcasting': '施法',
    'Stealth': '潜行',
    'Stretching': '伸展',
    'Supernatural strength': '超自然力量',
    'Surfing': '冲浪',
    'Tail': '尾巴',
    'Tech genius': '科技天才',
    'Technopath': '科技感应',
    'Time travel': '时间旅行',
    'Unbreakable skin': '不坏之肤',
    'Unknown': '未知',
    'Vampire strengths': '吸血鬼之力',
    'Vibranium technology': '振金科技',
    'Weapon generation': '武器生成',
    'Weapon systems': '武器系统',
    'Weapons master': '武器大师',
    'Yaka arrow control': '亚卡箭操控',
    'Acrobat': '杂技',
    'Body manipulation': '身体操控',
    'Master assassin': '刺客大师',
    'Superhuman agility': '超人类敏捷',
    'Human/Celestial Hybrid': '人类/天神族混血',
    'Zen-Whoberian': '泽恩-沃伯里人',
    'Genetically Engineered Raccoon': '基因改造浣熊',
    'Flora Colossus': '植物巨人',
    'Luphomoid': '卢福莫伊人',
    'Centaurian': '半人马座人',
    'Olympian God': '奥林匹斯神',
    'Cosmic Entity Host': '宇宙实体宿主',
    'Human/Cosmic Entity': '人类/宇宙实体',
    'Cosmic Entity': '宇宙实体',
    'Human (Enhanced)': '人类（强化）',
    'Human (Gamma Mutate)': '人类（伽马突变）',
    'Mutant': '变种人',
    'Mutant (Enhanced)': '变种人（强化）',
    'Asgardian': '阿斯加德人',
    'Human': '人类',
    'Human (Rock-like)': '人类（岩石形态）',
    'Human (Silicate)': '人类（硅基）',
    'Human/Reptile Hybrid': '人类/爬行动物混血',
    'Vampire-Human Hybrid': '吸血鬼-人类混血',
    'Human (Demon Bond)': '人类（恶魔契约）',
}

def translate_abilities(line):
    """Translate abilities field in a line."""
    if 'abilities:' not in line:
        return line
    
    # Find abilities value
    match = re.search(r'(abilities: ")([^"]*)(")', line)
    if not match:
        return line
    
    abilities_str = match.group(2)
    
    # Split by comma
    ability_list = [a.strip() for a in abilities_str.split(',')]
    translated_list = []
    
    for ability in ability_list:
        if ability in ABILITIES:
            translated_list.append(ABILITIES[ability])
        else:
            # Try to find partial match
            found = False
            for eng, cn in ABILITIES.items():
                if eng in ability:
                    translated_list.append(cn)
                    found = True
                    break
            if not found:
                translated_list.append(ability)  # Keep original if no match
    
    new_line = line.replace(abilities_str, ', '.join(translated_list))
    return new_line

def main():
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    changes = 0
    
    for line in lines:
        if 'abilities:' in line and 'Character' in line:
            new_line = translate_abilities(line)
            if new_line != line:
                changes += 1
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    with open(CYPER_FILE, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Abilities translation complete!")
    print(f"Changed {changes} lines")
    
    # Verify
    print("\n=== Sample characters with abilities ===")
    import re
    for m in re.finditer(r'MERGE \(\w+:Character \{name_cn: "([^"]+)"[^}]*abilities: "([^"]*)"\}', content):
        if len(new_lines) > 5 and 'Character' in new_lines[5]:
            pass
        print(f"  {m.group(1)}: {m.group(2)[:80]}")
        break
    
    # Count remaining English
    remaining = 0
    for m in re.finditer(r'abilities: "([^"]*)"', '\n'.join(new_lines)):
        val = m.group(1)
        if re.search(r'[A-Z][a-z]+', val):
            remaining += 1
            print(f"  Still has English: {m.group(1)[:60]}")
    
    print(f"\nCharacters with remaining English in abilities: {remaining}")

if __name__ == '__main__':
    main()
