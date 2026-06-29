// ============================================================
// entities_characters_p1.cypher
// 第一批：c1 ~ c7 Character 节点
// 来源: import_data_clean_fixed.cypher (lines 3-9)
// ============================================================

MERGE (c1:Character {name_en: "Iron Man", name: "钢铁侠", real_name: "Anthony Edward Tony Stark", species: "人类", first_appearance: "Tales of Suspense #39 (March 1963)", abilities: "天才级智力, 动力装甲, 飞行, 冲击射线, 装甲强化力量"});
MERGE (c2:Character {name_en: "Captain America", name: "美国队长", real_name: "Steve Rogers", species: "人类(强化)", first_appearance: "Captain America Comics #1 (March 1941)", abilities: "超人类力量, 敏捷, 速度, 耐力, 大师级战术家, 振金盾牌专家"});
MERGE (c3:Character {name_en: "Thor", name: "雷神", real_name: "Thor Odinson", species: "阿斯加德人", first_appearance: "Journey into Mystery #83 (August 1962)", abilities: "超人类力量, 天气控制, 雷电操控, 飞行 (妙尔尼尔), 延长寿命"});
MERGE (c4:Character {name_en: "Hulk", name: "浩克", real_name: "Bruce Banner", species: "人类(伽马突变)", first_appearance: "The Incredible Hulk #1 (May 1962)", abilities: "无限力量, 再生治愈因子, 超人类耐力, 天才智力"});
MERGE (c5:Character {name_en: "Black Widow", name: "黑寡妇", real_name: "Natasha Romanoff", species: "人类(强化)", first_appearance: "Tales of Suspense #52 (April 1964)", abilities: "大师级间谍, 武术专家, 延缓衰老, 武器专家, 红房训练"});
MERGE (c6:Character {name_en: "Hawkeye", name: "鹰眼", real_name: "Clint Barton", species: "人类", first_appearance: "Tales of Suspense #57 (September 1964)", abilities: "大师级弓箭手, 神枪手, 大师级战术家, 徒手格斗, 特制箭矢"});
MERGE (c7:Character {name_en: "Nick Fury", name: "尼克·弗瑞", real_name: "Nicholas Joseph Fury", species: "人类", first_appearance: "Sgt. Fury and his Howling Commandos #1 (May 1963)", abilities: "大师级战略家, 战斗专家, 间谍大师, 领导力"});
