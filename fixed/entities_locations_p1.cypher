// ============================================================
// entities_locations_p1.cypher
// 第一批：c1 ~ c7 相关的 Location 节点 (l1 ~ l3)
// 来源: import_data_clean_fixed.cypher (lines 23-25)
// ============================================================

MERGE (l1:Location {name: "Asgard", type: "维度"});
MERGE (l2:Location {name: "New York City", type: "城市"});
MERGE (l3:Location {name: "Avengers Tower", type: "总部"});
