// p13_relationships.cypher

MATCH (c930:Character {name_en: 'Hawkeye (Kate Bishop)'}), (t11:Team {name_en: 'Young Avengers'})
MERGE (c930)-[:成员]->(t11);

MATCH (c931:Character {name_en: 'Wiccan'}), (t11:Team {name_en: 'Young Avengers'})
MERGE (c931)-[:成员]->(t11);

MATCH (c932:Character {name_en: 'Speed'}), (t11:Team {name_en: 'Young Avengers'})
MERGE (c932)-[:成员]->(t11);

MATCH (c933:Character {name_en: 'Stature'}), (t11:Team {name_en: 'Young Avengers'})
MERGE (c933)-[:成员]->(t11);

MATCH (c930:Character {name_en: 'Hawkeye (Kate Bishop)'}), (c6:Character {name_en: 'Hawkeye'})
MERGE (c930)-[:盟友]->(c6);

MATCH (c930:Character {name_en: 'Hawkeye (Kate Bishop)'}), (c6:Character {name_en: 'Hawkeye'})
MERGE (c6)-[:盟友]->(c930);
