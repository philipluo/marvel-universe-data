// ============================================================
// relationships_movie_appearances.cypher
// 电影-角色出演关系（Character → Movie）
// 使用 MATCH 按唯一属性定位已有节点，再用 MERGE 创建出演关系。
// ============================================================

// ============================================================
// 钢铁侠 (2008)
// ============================================================
MATCH (c:Character {name_en: "Iron Man"}), (m:Movie {title: "钢铁侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Pepper Potts"}), (m:Movie {title: "钢铁侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Happy Hogan"}), (m:Movie {title: "钢铁侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine"}), (m:Movie {title: "钢铁侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine (James Rhodes)"}), (m:Movie {title: "钢铁侠"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 无敌浩克 (2008)
// ============================================================
MATCH (c:Character {name_en: "Hulk"}), (m:Movie {title: "无敌浩克"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 钢铁侠2 (2010)
// ============================================================
MATCH (c:Character {name_en: "Iron Man"}), (m:Movie {title: "钢铁侠2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Pepper Potts"}), (m:Movie {title: "钢铁侠2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Happy Hogan"}), (m:Movie {title: "钢铁侠2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine"}), (m:Movie {title: "钢铁侠2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine (James Rhodes)"}), (m:Movie {title: "钢铁侠2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Black Widow"}), (m:Movie {title: "钢铁侠2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nick Fury"}), (m:Movie {title: "钢铁侠2"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 雷神 (2011)
// ============================================================
MATCH (c:Character {name_en: "Thor"}), (m:Movie {title: "雷神"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Loki"}), (m:Movie {title: "雷神"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Hawkeye"}), (m:Movie {title: "雷神"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 美国队长：复仇者先锋 (2011)
// ============================================================
MATCH (c:Character {name_en: "Captain America"}), (m:Movie {title: "美国队长：复仇者先锋"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Red Skull"}), (m:Movie {title: "美国队长：复仇者先锋"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Winter Soldier"}), (m:Movie {title: "美国队长：复仇者先锋"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 复仇者联盟 (2012)
// ============================================================
MATCH (c:Character {name_en: "Iron Man"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Captain America"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Thor"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Hulk"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Black Widow"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Hawkeye"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nick Fury"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Loki"}), (m:Movie {title: "复仇者联盟"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 钢铁侠3 (2013)
// ============================================================
MATCH (c:Character {name_en: "Iron Man"}), (m:Movie {title: "钢铁侠3"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Pepper Potts"}), (m:Movie {title: "钢铁侠3"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Happy Hogan"}), (m:Movie {title: "钢铁侠3"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine"}), (m:Movie {title: "钢铁侠3"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine (James Rhodes)"}), (m:Movie {title: "钢铁侠3"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Mandarin"}), (m:Movie {title: "钢铁侠3"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 美国队长2：冬日战士 (2014)
// ============================================================
MATCH (c:Character {name_en: "Captain America"}), (m:Movie {title: "美国队长2：冬日战士"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Winter Soldier"}), (m:Movie {title: "美国队长2：冬日战士"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Black Widow"}), (m:Movie {title: "美国队长2：冬日战士"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nick Fury"}), (m:Movie {title: "美国队长2：冬日战士"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Falcon"}), (m:Movie {title: "美国队长2：冬日战士"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Crossbones"}), (m:Movie {title: "美国队长2：冬日战士"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 银河护卫队 (2014)
// ============================================================
MATCH (c:Character {name_en: "Star-Lord"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Gamora"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Drax"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Rocket Raccoon"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Groot"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Thanos"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nebula"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ronan"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Yondu"}), (m:Movie {title: "银河护卫队"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 蚁人 (2015)
// ============================================================
MATCH (c:Character {name_en: "Ant-Man (Scott Lang)"}), (m:Movie {title: "蚁人"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ant-Man"}), (m:Movie {title: "蚁人"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ant-Man (Hank Pym)"}), (m:Movie {title: "蚁人"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Wasp (Hope Van Dyne)"}), (m:Movie {title: "蚁人"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Falcon"}), (m:Movie {title: "蚁人"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 奇异博士 (2016)
// ============================================================
MATCH (c:Character {name_en: "Doctor Strange"}), (m:Movie {title: "奇异博士"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 银河护卫队2 (2017)
// ============================================================
MATCH (c:Character {name_en: "Star-Lord"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Gamora"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Drax"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Rocket Raccoon"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Groot"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Mantis"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Yondu"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nebula"}), (m:Movie {title: "银河护卫队2"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 雷神3：诸神黄昏 (2017)
// ============================================================
MATCH (c:Character {name_en: "Thor"}), (m:Movie {title: "雷神3：诸神黄昏"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Loki"}), (m:Movie {title: "雷神3：诸神黄昏"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Hulk"}), (m:Movie {title: "雷神3：诸神黄昏"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Doctor Strange"}), (m:Movie {title: "雷神3：诸神黄昏"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 黑豹 (2018)
// ============================================================
MATCH (c:Character {name_en: "Black Panther"}), (m:Movie {title: "黑豹"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Shuri"}), (m:Movie {title: "黑豹"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Okoye"}), (m:Movie {title: "黑豹"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Winter Soldier"}), (m:Movie {title: "黑豹"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 复仇者联盟：无限战争 (2018)
// ============================================================
MATCH (c:Character {name_en: "Iron Man"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Spider-Man"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Doctor Strange"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Star-Lord"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Gamora"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Drax"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Rocket Raccoon"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Groot"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Mantis"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nebula"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Thanos"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Captain America"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Black Widow"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Scarlet Witch"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Falcon"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine (James Rhodes)"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Black Panther"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Shuri"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Okoye"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Winter Soldier"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Loki"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Thor"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Hulk"}), (m:Movie {title: "复仇者联盟：无限战争"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 蚁人2：黄蜂女现身 (2018)
// ============================================================
MATCH (c:Character {name_en: "Ant-Man (Scott Lang)"}), (m:Movie {title: "蚁人2：黄蜂女现身"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ant-Man"}), (m:Movie {title: "蚁人2：黄蜂女现身"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Wasp (Hope Van Dyne)"}), (m:Movie {title: "蚁人2：黄蜂女现身"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ant-Man (Hank Pym)"}), (m:Movie {title: "蚁人2：黄蜂女现身"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 惊奇队长 (2019)
// ============================================================
MATCH (c:Character {name_en: "Captain Marvel"}), (m:Movie {title: "惊奇队长"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nick Fury"}), (m:Movie {title: "惊奇队长"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 复仇者联盟：终局之战 (2019)
// ============================================================
MATCH (c:Character {name_en: "Iron Man"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Captain America"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Thor"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Hulk"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Black Widow"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Hawkeye"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Spider-Man"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Doctor Strange"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Black Panther"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Star-Lord"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Rocket Raccoon"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nebula"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Scarlet Witch"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Falcon"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "War Machine (James Rhodes)"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Winter Soldier"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Shuri"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Okoye"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ant-Man (Scott Lang)"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ant-Man"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Captain Marvel"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Thanos"}), (m:Movie {title: "复仇者联盟：终局之战"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 蜘蛛侠：英雄远征 (2019)
// ============================================================
MATCH (c:Character {name_en: "Spider-Man"}), (m:Movie {title: "蜘蛛侠：英雄远征"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Happy Hogan"}), (m:Movie {title: "蜘蛛侠：英雄远征"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Nick Fury"}), (m:Movie {title: "蜘蛛侠：英雄远征"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Mysterio"}), (m:Movie {title: "蜘蛛侠：英雄远征"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 蜘蛛侠：英雄无归 (2021)
// ============================================================
MATCH (c:Character {name_en: "Spider-Man"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Doctor Strange"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Ned Leeds"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "J. Jonah Jameson"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Aunt May"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Green Goblin"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Doc Ock"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Electro"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Sandman"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Lizard"}), (m:Movie {title: "蜘蛛侠：英雄无归"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 尚气与十环传奇 (2021)
// ============================================================
MATCH (c:Character {name_en: "Shang-Chi"}), (m:Movie {title: "尚气与十环传奇"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Mandarin"}), (m:Movie {title: "尚气与十环传奇"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 永恒族 (2021)
// ============================================================
// 本系统中的角色未出现在该电影中，暂不添加关系
// ============================================================

// ============================================================
// 蜘蛛侠 (2002) — 托比版
// ============================================================
MATCH (c:Character {name_en: "Spider-Man"}), (m:Movie {title: "蜘蛛侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Green Goblin"}), (m:Movie {title: "蜘蛛侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "J. Jonah Jameson"}), (m:Movie {title: "蜘蛛侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Mary Jane Watson"}), (m:Movie {title: "蜘蛛侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Aunt May"}), (m:Movie {title: "蜘蛛侠"})
MERGE (c)-[:出演]->(m);

// ============================================================
// X战警 (2000)
// ============================================================
MATCH (c:Character {name_en: "Professor X"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Cyclops"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Wolverine"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Storm"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Jean Grey"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Magneto"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Mystique"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Sabretooth"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Rogue"}), (m:Movie {title: "X战警"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 刀锋战士 (1998)
// ============================================================
MATCH (c:Character {name_en: "Blade"}), (m:Movie {title: "刀锋战士"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 夜魔侠 (2003)
// ============================================================
MATCH (c:Character {name_en: "Daredevil"}), (m:Movie {title: "夜魔侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Elektra"}), (m:Movie {title: "夜魔侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Kingpin"}), (m:Movie {title: "夜魔侠"})
MERGE (c)-[:出演]->(m);

// ============================================================
// 神奇四侠 (2005)
// ============================================================
MATCH (c:Character {name_en: "Mister Fantastic"}), (m:Movie {title: "神奇四侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Invisible Woman"}), (m:Movie {title: "神奇四侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "人类 Torch"}), (m:Movie {title: "神奇四侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "The Thing"}), (m:Movie {title: "神奇四侠"})
MERGE (c)-[:出演]->(m);
MATCH (c:Character {name_en: "Doctor Doom"}), (m:Movie {title: "神奇四侠"})
MERGE (c)-[:出演]->(m);
