// ============================================================
// entities_teams_p1.cypher
// 第一批：t1 ~ t3 Team 节点
// 来源: import_data_clean_fixed.cypher (lines 10-12)
//
// 字段改造: name → name_en, 新增 name 中文译名
// ============================================================

MERGE (t1:Team {name_en: "Avengers", name: "复仇者联盟", type: "超级英雄团队"});
MERGE (t2:Team {name_en: "S.H.I.E.L.D.", name: "神盾局", type: "情报机构"});
MERGE (t3:Team {name_en: "Stark Industries", name: "斯塔克工业", type: "科技公司"});
