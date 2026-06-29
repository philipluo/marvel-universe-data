// p15_relationships.cypher

MATCH (c950:Character {name_en: 'Happy Hogan'}), (t3:Team {name_en: 'Stark Industries'})
MERGE (c950)-[:成员]->(t3);

MATCH (c951:Character {name_en: 'Pepper Potts'}), (t3:Team {name_en: 'Stark Industries'})
MERGE (c951)-[:成员]->(t3);

MATCH (c951:Character {name_en: 'Pepper Potts'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c951)-[:盟友]->(c1);

MATCH (c951:Character {name_en: 'Pepper Potts'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c1)-[:盟友]->(c951);

MATCH (c954:Character {name_en: 'Wasp (Hope Van Dyne)'}), (c955:Character {name_en: 'Ant-Man (Hank Pym)'})
MERGE (c954)-[:亲属]->(c955);

MATCH (c955:Character {name_en: 'Ant-Man (Hank Pym)'}), (t1:Team {name_en: 'Avengers'})
MERGE (c955)-[:成员]->(t1);

MATCH (c954:Character {name_en: 'Wasp (Hope Van Dyne)'}), (t1:Team {name_en: 'Avengers'})
MERGE (c954)-[:成员]->(t1);
