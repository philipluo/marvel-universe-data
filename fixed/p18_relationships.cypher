// p18_relationships.cypher

MATCH (c980:Character {name_en: 'Absorbing Man'}), (c3:Character {name_en: 'Thor'})
MERGE (c980)-[:敌人]->(c3);

MATCH (c980:Character {name_en: 'Absorbing Man'}), (c3:Character {name_en: 'Thor'})
MERGE (c3)-[:敌人]->(c980);

MATCH (c982:Character {name_en: 'Taskmaster'}), (t1:Team {name_en: 'Avengers'})
MERGE (c982)-[:敌人]->(t1);

MATCH (c982:Character {name_en: 'Taskmaster'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:敌人]->(c982);
