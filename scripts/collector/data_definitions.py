#!/usr/bin/env python3
"""
data_definitions.py — 漫威待收集数据定义

按批次组织。每次 run_batch.py 从中取一批生成 Cypher 文件。
关系定义通过 name_en 引用实体（已存在或本批新增的）。
"""

# ============================================================
# 批次定义
# ============================================================
# 每个批次是一个 dict:
#   "name": 批次名称
#   "characters": [{"name_en": ..., "name": ..., "real_name": ..., ...}, ...]
#   "teams": [{"name_en": ..., "name": ..., "type": ...}, ...]
#   "locations": [{"name": ..., "type": ...}, ...]
#   "movies": [{"title": ..., "year": ...}, ...]
#   "events": [{"event_name": ..., "year": ...}, ...]
#   "items": [{"item_name": ..., "type": ...}, ...]
#   "relationships": [
#       (src_name_en, src_label, rel_type, tgt_name_en, tgt_label, bidirectional),
#       ...
#   ]

BATCHES = [
    # ============================================================
    # Batch 1: 蜘蛛侠宇宙扩展 + 更多 X-Men + 新反派
    # ============================================================
    {
        "name": "Spider-Verse & More X-Men & New Villains",
        "characters": [
            # --- 蜘蛛侠宇宙 ---
            {
                "name_en": "Miles Morales",
                "name": "迈尔斯·莫拉莱斯",
                "real_name": "Miles Morales",
                "species": "人类(强化)",
                "first_appearance": "Ultimate Fallout #4 (August 2011)",
                "abilities": "蜘蛛感应, 壁虎攀爬, 隐身, 毒刺冲击, 摆荡, 超人类力量",
            },
            {
                "name_en": "Spider-Gwen",
                "name": "蜘蛛格温",
                "real_name": "Gwen Stacy",
                "species": "人类(强化)",
                "first_appearance": "Edge of Spider-Verse #2 (September 2014)",
                "abilities": "蜘蛛感应, 壁虎攀爬, 摆荡, 超人类力量, 敏捷",
            },
            {
                "name_en": "Kraven the Hunter",
                "name": "猎人克莱文",
                "real_name": "Sergei Kravinoff",
                "species": "人类(强化)",
                "first_appearance": "Amazing Spider-Man #15 (August 1964)",
                "abilities": "增强力量, 敏捷, 耐力, 狩猎大师, 追踪专家, 草药强化",
            },
            {
                "name_en": "Rhino",
                "name": "犀牛人",
                "real_name": "Aleksei Sytsevich",
                "species": "人类(强化)",
                "first_appearance": "Amazing Spider-Man #41 (October 1966)",
                "abilities": "超人类力量, 坚不可摧皮肤, 冲撞攻击, 耐力强化",
            },
            {
                "name_en": "Aunt May",
                "name": "梅婶",
                "real_name": "May Parker",
                "species": "人类",
                "first_appearance": "Amazing Fantasy #15 (August 1962)",
                "abilities": "关爱, 支持, 智慧",
            },
            # --- 更多 X-Men ---
            {
                "name_en": "Jubilee",
                "name": "欢欢/jubilee",
                "real_name": "Jubilation Lee",
                "species": "变种人",
                "first_appearance": "Uncanny X-Men #244 (May 1989)",
                "abilities": "烟花能量爆破, 飞行, 能量免疫, 火光操控",
            },
            {
                "name_en": "Polaris",
                "name": "北极星",
                "real_name": "Lorna Dane",
                "species": "变种人",
                "first_appearance": "Uncanny X-Men #49 (October 1968)",
                "abilities": "磁场操控, 金属操控, 电磁场生成, 飞行",
            },
            {
                "name_en": "Havok",
                "name": "冲击波",
                "real_name": "Alex Summers",
                "species": "变种人",
                "first_appearance": "Uncanny X-Men #54 (March 1969)",
                "abilities": "等离子能量吸收与释放, 冲击波, 能量操控, 热能抵抗",
            },
            {
                "name_en": "Forge",
                "name": "锻工",
                "real_name": "Forge",
                "species": "变种人",
                "first_appearance": "Uncanny X-Men #184 (August 1984)",
                "abilities": "天才发明家, 机械工程, 魔法感知, 科技创造",
            },
            # --- 新反派 ---
            {
                "name_en": "Kang the Conqueror",
                "name": "征服者康",
                "real_name": "Nathaniel Richards",
                "species": "人类(强化)",
                "first_appearance": "Avengers #8 (September 1964)",
                "abilities": "时间旅行, 超级科技装甲, 天才智力, 能量投射, 时间操控",
            },
            {
                "name_en": "Baron Zemo",
                "name": "泽莫男爵",
                "real_name": "Helmut Zemo",
                "species": "人类",
                "first_appearance": "Avengers #6 (July 1964)",
                "abilities": "天才智力, 战略大师, 战斗专家, 武器大师",
            },
            {
                "name_en": "M.O.D.O.K.",
                "name": "魔多客",
                "real_name": "George Tarleton",
                "species": "人类(变异)",
                "first_appearance": "Tales of Suspense #93 (September 1967)",
                "abilities": "超级大脑, 心灵力量, 能量投射, 力场生成, 飞行座椅",
            },
            {
                "name_en": "Bullseye",
                "name": "靶眼",
                "real_name": "Benjamin Poindexter",
                "species": "人类",
                "first_appearance": "Daredevil #131 (March 1976)",
                "abilities": "百发百中投掷, 物品武器化, 大师级战斗, 致命精准",
            },
        ],
        "teams": [
            {
                "name_en": "Thunderbolts",
                "name": "雷霆特工队",
                "type": "反派转型团队",
            },
        ],
        "locations": [
            {
                "name": "Negative Zone",
                "type": "反物质维度",
            },
            {
                "name": "Limbo",
                "type": "地狱维度",
            },
            {
                "name": "Battleworld",
                "type": "拼接星球",
            },
        ],
        "movies": [
            {
                "title": "蜘蛛侠：纵横宇宙",
                "year": "2023",
            },
            {
                "title": "蜘蛛侠：超越宇宙",
                "year": "2024",
            },
        ],
        "events": [
            {
                "event_name": "蜘蛛宇宙",
                "year": "2014",
            },
            {
                "event_name": "善恶轴心",
                "year": "2014",
            },
        ],
        "items": [
            {
                "item_name": "Venom Symbiote",
                "type": "共生体",
            },
            {
                "item_name": "Kang's Time Chair",
                "type": "时间科技",
            },
        ],
        "relationships": [
            # 蜘蛛侠宇宙角色之间的关系
            ("Miles Morales", "Character", "盟友", "Spider-Man", "Character", True),
            ("Miles Morales", "Character", "盟友", "Spider-Gwen", "Character", True),
            ("Miles Morales", "Character", "盟友", "Captain America", "Character", True),
            ("Miles Morales", "Character", "盟友", "Iron Man", "Character", True),
            ("Miles Morales", "Character", "成员", "Avengers", "Team", False),
            ("Spider-Gwen", "Character", "盟友", "Spider-Man", "Character", True),
            ("Kraven the Hunter", "Character", "敌人", "Spider-Man", "Character", True),
            ("Rhino", "Character", "敌人", "Spider-Man", "Character", True),
            ("Aunt May", "Character", "亲属", "Spider-Man", "Character", False),
            ("Aunt May", "Character", "盟友", "Iron Man", "Character", False),
            # X-Men 关系
            ("Jubilee", "Character", "成员", "X-Men", "Team", False),
            ("Jubilee", "Character", "盟友", "Wolverine", "Character", True),
            ("Polaris", "Character", "成员", "X-Men", "Team", False),
            ("Polaris", "Character", "亲属", "Magneto", "Character", False),
            ("Havok", "Character", "成员", "X-Men", "Team", False),
            ("Havok", "Character", "亲属", "Cyclops", "Character", False),
            ("Forge", "Character", "成员", "X-Men", "Team", False),
            ("Forge", "Character", "盟友", "Storm", "Character", True),
            # 反派关系
            ("Kang the Conqueror", "Character", "敌人", "Avengers", "Team", True),
            ("Kang the Conqueror", "Character", "敌人", "Iron Man", "Character", True),
            ("Kang the Conqueror", "Character", "敌人", "Captain America", "Character", True),
            ("Kang the Conqueror", "Character", "敌人", "Fantastic Four", "Team", True),
            ("Baron Zemo", "Character", "敌人", "Captain America", "Character", True),
            ("Baron Zemo", "Character", "敌人", "Avengers", "Team", True),
            ("Baron Zemo", "Character", "成员", "Thunderbolts", "Team", False),
            ("M.O.D.O.K.", "Character", "敌人", "Captain America", "Character", True),
            ("M.O.D.O.K.", "Character", "敌人", "Avengers", "Team", True),
            ("Bullseye", "Character", "敌人", "Daredevil", "Character", True),
            ("Bullseye", "Character", "敌人", "Punisher", "Character", True),
        ],
    },

    # ============================================================
    # Batch 2: 宇宙扩展 + 更多英雄 + 更多关系
    # ============================================================
    {
        "name": "Cosmic Expansion & More Heroes",
        "characters": [
            {
                "name_en": "Nova",
                "name": "新星",
                "real_name": "Richard Rider",
                "species": "人类(强化)",
                "first_appearance": "Nova #1 (September 1976)",
                "abilities": "超人类力量, 飞行, 能量吸收与投射, 宇宙感知, 速度",
            },
            {
                "name_en": "Adam Warlock",
                "name": "亚当术士",
                "real_name": "Adam Warlock",
                "species": "人造人",
                "first_appearance": "Fantastic Four #66 (September 1967)",
                "abilities": "能量操控, 飞行, 宇宙感知, 再生, 能量吸收",
            },
            {
                "name_en": "Quasar",
                "name": "类星体",
                "real_name": "Wendell Vaughn",
                "species": "人类(强化)",
                "first_appearance": "Captain America #217 (January 1978)",
                "abilities": "量子能量操控, 力场生成, 飞行, 能量投射, 宇宙力量",
            },
            {
                "name_en": "Gladiator",
                "name": "角斗士",
                "real_name": "Kallark",
                "species": "什叶尔人",
                "first_appearance": "X-Men #107 (October 1977)",
                "abilities": "超人类力量, 飞行, 热视力, 刀枪不入, 超速度",
            },
            {
                "name_en": "Bishop",
                "name": "毕肖普",
                "real_name": "Lucas Bishop",
                "species": "变种人",
                "first_appearance": "Uncanny X-Men #282 (November 1991)",
                "abilities": "能量吸收, 能量反弹, 未来预测, 武器大师",
            },
            {
                "name_en": "Spectrum",
                "name": "光谱",
                "real_name": "Monica Rambeau",
                "species": "人类(强化)",
                "first_appearance": "Amazing Spider-Man Annual #16 (1982)",
                "abilities": "能量转化, 光速飞行, 非物质化, 能量操控, 形态变化",
            },
            {
                "name_en": "White Tiger",
                "name": "白虎",
                "real_name": "Aya Ayala",
                "species": "人类(强化)",
                "first_appearance": "Free Comic Book Day: The Amazing Spider-Man #1 (2012)",
                "abilities": "超人类力量, 敏捷, 虎爪, 增强感官, 战斗专家",
            },
            {
                "name_en": "Black Cat",
                "name": "黑猫",
                "real_name": "Felicia Hardy",
                "species": "人类(强化)",
                "first_appearance": "Amazing Spider-Man #194 (July 1979)",
                "abilities": "运气操控, 超人类敏捷, 盗窃大师, 格斗专家, 钩爪",
            },
            {
                "name_en": "Mister Sinister",
                "name": "凶兆先生",
                "real_name": "Nathaniel Essex",
                "species": "变种人(强化)",
                "first_appearance": "Uncanny X-Men #221 (September 1987)",
                "abilities": "超人类力量, 再生, 心灵感应, 基因操控, 变形",
            },
            {
                "name_en": "Juggernaut",
                "name": "剑圣",
                "real_name": "Cain Marko",
                "species": "人类(强化)",
                "first_appearance": "Uncanny X-Men #12 (July 1965)",
                "abilities": "不可阻挡冲撞, 超人类力量, 刀枪不入, 力场生成, 耐力无限",
            },
        ],
        "relationships": [
            # 宇宙关系
            ("Nova", "Character", "盟友", "Star-Lord", "Character", True),
            ("Nova", "Character", "盟友", "Guardians of the Galaxy", "Team", False),
            ("Nova", "Character", "盟友", "Thor", "Character", True),
            ("Adam Warlock", "Character", "盟友", "Guardians of the Galaxy", "Team", False),
            ("Adam Warlock", "Character", "盟友", "Thanos", "Character", True),
            ("Adam Warlock", "Character", "盟友", "Silver Surfer", "Character", True),
            ("Quasar", "Character", "盟友", "Avengers", "Team", False),
            ("Quasar", "Character", "盟友", "Captain Marvel", "Character", True),
            ("Gladiator", "Character", "敌人", "Avengers", "Team", True),
            ("Gladiator", "Character", "盟友", "X-Men", "Team", False),
            ("Gladiator", "Character", "敌人", "Silver Surfer", "Character", True),
            ("Gladiator", "Character", "敌人", "Galactus", "Character", False),
            # X-Men 关系
            ("Bishop", "Character", "成员", "X-Men", "Team", False),
            ("Bishop", "Character", "盟友", "Professor X", "Character", True),
            ("Bishop", "Character", "盟友", "Cyclops", "Character", True),
            ("Mister Sinister", "Character", "敌人", "X-Men", "Team", True),
            ("Mister Sinister", "Character", "敌人", "Cyclops", "Character", True),
            ("Mister Sinister", "Character", "敌人", "Jean Grey", "Character", True),
            ("Juggernaut", "Character", "敌人", "X-Men", "Team", True),
            ("Juggernaut", "Character", "敌人", "Professor X", "Character", False),
            ("Juggernaut", "Character", "亲属", "Professor X", "Character", False),
            # 街头关系
            ("Spectrum", "Character", "盟友", "Avengers", "Team", False),
            ("Spectrum", "Character", "盟友", "Captain Marvel", "Character", True),
            ("White Tiger", "Character", "盟友", "Spider-Man", "Character", True),
            ("White Tiger", "Character", "盟友", "Daredevil", "Character", True),
            ("Black Cat", "Character", "盟友", "Spider-Man", "Character", True),
            ("Black Cat", "Character", "敌人", "Kingpin", "Character", True),
        ],
    },
]
