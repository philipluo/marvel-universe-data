// ============================================================
// relationships_p1.cypher
// 第一批：c1 ~ c7 相关的所有关系
// 来源: import_data_clean_fixed.cypher (lines 26-35, 36-42, 43-44)
//
// 注意：使用 MATCH 按唯一属性定位已有节点，再用 MERGE 创建关系。
// 不要直接写 MERGE (c1)-[:MEMBER_OF]->(t1)，这会导致创建空节点。
// ============================================================

// --- MEMBER_OF ---
MATCH (c1:Character {name_en: "Iron Man"}), (t1:Team {name_en: "Avengers"})
MERGE (c1)-[:MEMBER_OF]->(t1);

MATCH (c1:Character {name_en: "Iron Man"}), (t3:Team {name_en: "Stark Industries"})
MERGE (c1)-[:MEMBER_OF]->(t3);

MATCH (c2:Character {name_en: "Captain America"}), (t1:Team {name_en: "Avengers"})
MERGE (c2)-[:MEMBER_OF]->(t1);

MATCH (c3:Character {name_en: "Thor"}), (t1:Team {name_en: "Avengers"})
MERGE (c3)-[:MEMBER_OF]->(t1);

MATCH (c4:Character {name_en: "Hulk"}), (t1:Team {name_en: "Avengers"})
MERGE (c4)-[:MEMBER_OF]->(t1);

MATCH (c5:Character {name_en: "Black Widow"}), (t1:Team {name_en: "Avengers"})
MERGE (c5)-[:MEMBER_OF]->(t1);

MATCH (c5:Character {name_en: "Black Widow"}), (t2:Team {name_en: "S.H.I.E.L.D."})
MERGE (c5)-[:MEMBER_OF]->(t2);

MATCH (c6:Character {name_en: "Hawkeye"}), (t1:Team {name_en: "Avengers"})
MERGE (c6)-[:MEMBER_OF]->(t1);

MATCH (c6:Character {name_en: "Hawkeye"}), (t2:Team {name_en: "S.H.I.E.L.D."})
MERGE (c6)-[:MEMBER_OF]->(t2);

MATCH (c7:Character {name_en: "Nick Fury"}), (t2:Team {name_en: "S.H.I.E.L.D."})
MERGE (c7)-[:MEMBER_OF]->(t2);

// --- USES ---
MATCH (c2:Character {name_en: "Captain America"}), (i1:Item {name: "振金盾牌"})
MERGE (c2)-[:USES]->(i1);

MATCH (c3:Character {name_en: "Thor"}), (i2:Item {name: "妙尔尼尔(雷神之锤)"})
MERGE (c3)-[:USES]->(i2);

MATCH (c1:Character {name_en: "Iron Man"}), (i3:Item {name: "钢铁侠战甲"})
MERGE (c1)-[:USES]->(i3);

MATCH (c1:Character {name_en: "Iron Man"}), (i4:Item {name: "弧反应堆"})
MERGE (c1)-[:USES]->(i4);

MATCH (c5:Character {name_en: "Black Widow"}), (i5:Item {name: "寡妇之吻"})
MERGE (c5)-[:USES]->(i5);

MATCH (c6:Character {name_en: "Hawkeye"}), (i6:Item {name: "鹰眼弓"})
MERGE (c6)-[:USES]->(i6);

MATCH (c6:Character {name_en: "Hawkeye"}), (i7:Item {name: "特制箭矢"})
MERGE (c6)-[:USES]->(i7);

// --- ALLY_OF ---
MATCH (c1:Character {name_en: "Iron Man"}), (c2:Character {name_en: "Captain America"})
MERGE (c1)-[:ALLY_OF]->(c2);

MATCH (c3:Character {name_en: "Thor"}), (c4:Character {name_en: "Hulk"})
MERGE (c3)-[:ALLY_OF]->(c4);
