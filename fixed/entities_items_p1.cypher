// ============================================================
// entities_items_p1.cypher
// 第一批：c1 ~ c7 相关的 Item 节点 (i1 ~ i7)
// 来源: import_data_clean_fixed.cypher (lines 16-22)
// ============================================================

MERGE (i1:Item {name: "振金盾牌", type: "武器/防御"});
MERGE (i2:Item {name: "妙尔尼尔(雷神之锤)", type: "武器"});
MERGE (i3:Item {name: "钢铁侠战甲", type: "动力装甲"});
MERGE (i4:Item {name: "弧反应堆", type: "能源核心"});
MERGE (i5:Item {name: "寡妇之吻", type: "武器"});
MERGE (i6:Item {name: "鹰眼弓", type: "武器"});
MERGE (i7:Item {name: "特制箭矢", type: "弹药"});
