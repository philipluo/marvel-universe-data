// p4_relationships.cypher

MATCH (c300:Character {name_en: 'Thanos'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c300)-[:敌人]->(c1);

MATCH (c300:Character {name_en: 'Thanos'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c1)-[:敌人]->(c300);

MATCH (c300:Character {name_en: 'Thanos'}), (c2:Character {name_en: 'Captain America'})
MERGE (c300)-[:敌人]->(c2);

MATCH (c300:Character {name_en: 'Thanos'}), (c2:Character {name_en: 'Captain America'})
MERGE (c2)-[:敌人]->(c300);

MATCH (c300:Character {name_en: 'Thanos'}), (t1:Team {name_en: 'Avengers'})
MERGE (c300)-[:敌人]->(t1);

MATCH (c300:Character {name_en: 'Thanos'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:敌人]->(c300);

MATCH (c301:Character {name_en: 'Loki'}), (c3:Character {name_en: 'Thor'})
MERGE (c301)-[:敌人]->(c3);

MATCH (c301:Character {name_en: 'Loki'}), (c3:Character {name_en: 'Thor'})
MERGE (c3)-[:敌人]->(c301);

MATCH (c301:Character {name_en: 'Loki'}), (c2:Character {name_en: 'Captain America'})
MERGE (c301)-[:敌人]->(c2);

MATCH (c301:Character {name_en: 'Loki'}), (c2:Character {name_en: 'Captain America'})
MERGE (c2)-[:敌人]->(c301);

MATCH (c302:Character {name_en: 'Doctor Doom'}), (t4:Team {name_en: 'Fantastic Four'})
MERGE (c302)-[:敌人]->(t4);

MATCH (c302:Character {name_en: 'Doctor Doom'}), (t4:Team {name_en: 'Fantastic Four'})
MERGE (t4)-[:敌人]->(c302);

MATCH (c303:Character {name_en: 'Green Goblin'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c303)-[:敌人]->(c100);

MATCH (c303:Character {name_en: 'Green Goblin'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c303);

MATCH (c304:Character {name_en: 'Red Skull'}), (c2:Character {name_en: 'Captain America'})
MERGE (c304)-[:敌人]->(c2);

MATCH (c304:Character {name_en: 'Red Skull'}), (c2:Character {name_en: 'Captain America'})
MERGE (c2)-[:敌人]->(c304);

MATCH (c305:Character {name_en: 'Ultron'}), (t1:Team {name_en: 'Avengers'})
MERGE (c305)-[:敌人]->(t1);

MATCH (c305:Character {name_en: 'Ultron'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:敌人]->(c305);

MATCH (c306:Character {name_en: 'Venom'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c306)-[:敌人]->(c100);

MATCH (c306:Character {name_en: 'Venom'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c306);

MATCH (c202:Character {name_en: 'Wolverine'}), (c301:Character {name_en: 'Loki'})
MERGE (c202)-[:敌人]->(c301);

MATCH (c202:Character {name_en: 'Wolverine'}), (c301:Character {name_en: 'Loki'})
MERGE (c301)-[:敌人]->(c202);

MATCH (c3:Character {name_en: 'Thor'}), (c301:Character {name_en: 'Loki'})
MERGE (c3)-[:盟友]->(c301);

MATCH (c3:Character {name_en: 'Thor'}), (c301:Character {name_en: 'Loki'})
MERGE (c301)-[:盟友]->(c3);

MATCH (c302:Character {name_en: 'Doctor Doom'}), (l11:Location {name: 'Latveria'})
MERGE (c302)-[:来自]->(l11);

MATCH (c305:Character {name_en: 'Ultron'}), (i101:Item {item_name: 'Mind Stone'})
MERGE (c305)-[:使用]->(i101);

MATCH (c300:Character {name_en: 'Thanos'}), (i106:Item {item_name: 'Infinity Gauntlet'})
MERGE (c300)-[:使用]->(i106);

MATCH (c406:Character {name_en: 'Nebula'}), (c300:Character {name_en: 'Thanos'})
MERGE (c406)-[:敌人]->(c300);

MATCH (c406:Character {name_en: 'Nebula'}), (c300:Character {name_en: 'Thanos'})
MERGE (c300)-[:敌人]->(c406);

MATCH (c402:Character {name_en: 'Drax'}), (c300:Character {name_en: 'Thanos'})
MERGE (c402)-[:敌人]->(c300);

MATCH (c402:Character {name_en: 'Drax'}), (c300:Character {name_en: 'Thanos'})
MERGE (c300)-[:敌人]->(c402);

MATCH (c900:Character {name_en: 'Captain Universe'}), (c300:Character {name_en: 'Thanos'})
MERGE (c900)-[:敌人]->(c300);

MATCH (c900:Character {name_en: 'Captain Universe'}), (c300:Character {name_en: 'Thanos'})
MERGE (c300)-[:敌人]->(c900);

MATCH (c305:Character {name_en: 'Ultron'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c305)-[:敌人]->(c1);

MATCH (c1:Character {name_en: 'Iron Man'}), (c305:Character {name_en: 'Ultron'})
MERGE (c1)-[:敌人]->(c305);

MATCH (c302:Character {name_en: 'Doctor Doom'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c302)-[:敌人]->(c1);

MATCH (c1:Character {name_en: 'Iron Man'}), (c302:Character {name_en: 'Doctor Doom'})
MERGE (c1)-[:敌人]->(c302);
