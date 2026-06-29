// p2_characters.cypher

MERGE (c100:Character {name_en: "Spider-Man", name: "蜘蛛侠", real_name: "Peter Parker", species: "人类(强化)", first_appearance: "Amazing Fantasy #15 (August 1962)", abilities: "壁虎攀爬, 超人类力量, 蜘蛛感应, 摆荡"});

MERGE (c101:Character {name_en: "Doctor Strange", name: "奇异博士", real_name: "Stephen Strange", species: "人类", first_appearance: "Strange Tales #110 (July 1963)", abilities: "秘术大师, 时间操控, 灵体投射, 传送"});

MERGE (c102:Character {name_en: "Black Panther", name: "黑豹", real_name: "T'Challa", species: "人类(强化)", first_appearance: "Fantastic Four #52 (July 1966)", abilities: "超人类力量 (心形草), 天才智力, 振金战衣, 战斗大师"});

MERGE (c103:Character {name_en: "Captain Marvel", name: "惊奇队长", real_name: "Carol Danvers", species: "人类/克里混血", first_appearance: "Marvel Super-Heroes #13 (March 1968)", abilities: "超人类力量, 飞行, 能量投射, 光子冲击, 宇宙感知"});

MERGE (c104:Character {name_en: "Ant-Man", name: "蚁人", real_name: "Scott Lang", species: "人类", first_appearance: "Avengers #181 (March 1979)", abilities: "大小操控, 昆虫沟通, 超人类力量 when small"});

MERGE (c105:Character {name_en: "Scarlet Witch", name: "绯红女巫", real_name: "Wanda Maximoff", species: "人类(强化)", first_appearance: "X-Men #4 (March 1964)", abilities: "现实扭曲, 混沌魔法, 念力, 心灵操控"});

MERGE (c106:Character {name_en: "Falcon", name: "猎鹰", real_name: "Sam Wilson", species: "人类", first_appearance: "Captain America #117 (September 1968)", abilities: "飞行 via mechanical wings, 鸟类心灵链接, 战斗专家"});

MERGE (c107:Character {name_en: "War Machine", name: "战争机器", real_name: "James Rhodes", species: "人类", first_appearance: "Iron Man #118 (January 1979)", abilities: "动力装甲, 飞行, 多种武器系统, 超人类力量"});
