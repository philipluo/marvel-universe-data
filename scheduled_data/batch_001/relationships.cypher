// relationships.cypher — Batch 1
// 29 条关系

MATCH (c984:Character {name_en: "Miles Morales"}), (c100:Character {name_en: "Spider-Man"})
MERGE (c984)-[:盟友]->(c100);
MATCH (c100:Character {name_en: "Spider-Man"}), (c984:Character {name_en: "Miles Morales"})
MERGE (c100)-[:盟友]->(c984);
MATCH (c984:Character {name_en: "Miles Morales"}), (c985:Character {name_en: "Spider-Gwen"})
MERGE (c984)-[:盟友]->(c985);
MATCH (c985:Character {name_en: "Spider-Gwen"}), (c984:Character {name_en: "Miles Morales"})
MERGE (c985)-[:盟友]->(c984);
MATCH (c984:Character {name_en: "Miles Morales"}), (c2:Character {name_en: "Captain America"})
MERGE (c984)-[:盟友]->(c2);
MATCH (c2:Character {name_en: "Captain America"}), (c984:Character {name_en: "Miles Morales"})
MERGE (c2)-[:盟友]->(c984);
MATCH (c984:Character {name_en: "Miles Morales"}), (c1:Character {name_en: "Iron Man"})
MERGE (c984)-[:盟友]->(c1);
MATCH (c1:Character {name_en: "Iron Man"}), (c984:Character {name_en: "Miles Morales"})
MERGE (c1)-[:盟友]->(c984);
MATCH (c984:Character {name_en: "Miles Morales"}), (t1:Team {name_en: "Avengers"})
MERGE (c984)-[:成员]->(t1);
MATCH (c985:Character {name_en: "Spider-Gwen"}), (c100:Character {name_en: "Spider-Man"})
MERGE (c985)-[:盟友]->(c100);
MATCH (c100:Character {name_en: "Spider-Man"}), (c985:Character {name_en: "Spider-Gwen"})
MERGE (c100)-[:盟友]->(c985);
MATCH (c986:Character {name_en: "Kraven the Hunter"}), (c100:Character {name_en: "Spider-Man"})
MERGE (c986)-[:敌人]->(c100);
MATCH (c100:Character {name_en: "Spider-Man"}), (c986:Character {name_en: "Kraven the Hunter"})
MERGE (c100)-[:敌人]->(c986);
MATCH (c987:Character {name_en: "Rhino"}), (c100:Character {name_en: "Spider-Man"})
MERGE (c987)-[:敌人]->(c100);
MATCH (c100:Character {name_en: "Spider-Man"}), (c987:Character {name_en: "Rhino"})
MERGE (c100)-[:敌人]->(c987);
MATCH (c988:Character {name_en: "Aunt May"}), (c100:Character {name_en: "Spider-Man"})
MERGE (c988)-[:亲属]->(c100);
MATCH (c988:Character {name_en: "Aunt May"}), (c1:Character {name_en: "Iron Man"})
MERGE (c988)-[:盟友]->(c1);
MATCH (c989:Character {name_en: "Jubilee"}), (t5:Team {name_en: "X-Men"})
MERGE (c989)-[:成员]->(t5);
MATCH (c989:Character {name_en: "Jubilee"}), (c202:Character {name_en: "Wolverine"})
MERGE (c989)-[:盟友]->(c202);
MATCH (c202:Character {name_en: "Wolverine"}), (c989:Character {name_en: "Jubilee"})
MERGE (c202)-[:盟友]->(c989);
MATCH (c990:Character {name_en: "Polaris"}), (t5:Team {name_en: "X-Men"})
MERGE (c990)-[:成员]->(t5);
MATCH (c990:Character {name_en: "Polaris"}), (c205:Character {name_en: "Magneto"})
MERGE (c990)-[:亲属]->(c205);
MATCH (c991:Character {name_en: "Havok"}), (t5:Team {name_en: "X-Men"})
MERGE (c991)-[:成员]->(t5);
MATCH (c991:Character {name_en: "Havok"}), (c201:Character {name_en: "Cyclops"})
MERGE (c991)-[:亲属]->(c201);
MATCH (c992:Character {name_en: "Forge"}), (t5:Team {name_en: "X-Men"})
MERGE (c992)-[:成员]->(t5);
MATCH (c992:Character {name_en: "Forge"}), (c203:Character {name_en: "Storm"})
MERGE (c992)-[:盟友]->(c203);
MATCH (c203:Character {name_en: "Storm"}), (c992:Character {name_en: "Forge"})
MERGE (c203)-[:盟友]->(c992);
MATCH (c993:Character {name_en: "Kang the Conqueror"}), (t1:Team {name_en: "Avengers"})
MERGE (c993)-[:敌人]->(t1);
MATCH (t1:Team {name_en: "Avengers"}), (c993:Character {name_en: "Kang the Conqueror"})
MERGE (t1)-[:敌人]->(c993);
MATCH (c993:Character {name_en: "Kang the Conqueror"}), (c1:Character {name_en: "Iron Man"})
MERGE (c993)-[:敌人]->(c1);
MATCH (c1:Character {name_en: "Iron Man"}), (c993:Character {name_en: "Kang the Conqueror"})
MERGE (c1)-[:敌人]->(c993);
MATCH (c993:Character {name_en: "Kang the Conqueror"}), (c2:Character {name_en: "Captain America"})
MERGE (c993)-[:敌人]->(c2);
MATCH (c2:Character {name_en: "Captain America"}), (c993:Character {name_en: "Kang the Conqueror"})
MERGE (c2)-[:敌人]->(c993);
MATCH (c993:Character {name_en: "Kang the Conqueror"}), (t8:Team {name_en: "Fantastic Four"})
MERGE (c993)-[:敌人]->(t8);
MATCH (t8:Team {name_en: "Fantastic Four"}), (c993:Character {name_en: "Kang the Conqueror"})
MERGE (t8)-[:敌人]->(c993);
MATCH (c994:Character {name_en: "Baron Zemo"}), (c2:Character {name_en: "Captain America"})
MERGE (c994)-[:敌人]->(c2);
MATCH (c2:Character {name_en: "Captain America"}), (c994:Character {name_en: "Baron Zemo"})
MERGE (c2)-[:敌人]->(c994);
MATCH (c994:Character {name_en: "Baron Zemo"}), (t1:Team {name_en: "Avengers"})
MERGE (c994)-[:敌人]->(t1);
MATCH (t1:Team {name_en: "Avengers"}), (c994:Character {name_en: "Baron Zemo"})
MERGE (t1)-[:敌人]->(c994);
MATCH (c994:Character {name_en: "Baron Zemo"}), (t17:Team {name_en: "Thunderbolts"})
MERGE (c994)-[:成员]->(t17);
MATCH (c995:Character {name_en: "M.O.D.O.K."}), (c2:Character {name_en: "Captain America"})
MERGE (c995)-[:敌人]->(c2);
MATCH (c2:Character {name_en: "Captain America"}), (c995:Character {name_en: "M.O.D.O.K."})
MERGE (c2)-[:敌人]->(c995);
MATCH (c995:Character {name_en: "M.O.D.O.K."}), (t1:Team {name_en: "Avengers"})
MERGE (c995)-[:敌人]->(t1);
MATCH (t1:Team {name_en: "Avengers"}), (c995:Character {name_en: "M.O.D.O.K."})
MERGE (t1)-[:敌人]->(c995);
MATCH (c996:Character {name_en: "Bullseye"}), (c609:Character {name_en: "Daredevil"})
MERGE (c996)-[:敌人]->(c609);
MATCH (c609:Character {name_en: "Daredevil"}), (c996:Character {name_en: "Bullseye"})
MERGE (c609)-[:敌人]->(c996);
MATCH (c996:Character {name_en: "Bullseye"}), (c608:Character {name_en: "Punisher"})
MERGE (c996)-[:敌人]->(c608);
MATCH (c608:Character {name_en: "Punisher"}), (c996:Character {name_en: "Bullseye"})
MERGE (c608)-[:敌人]->(c996);
