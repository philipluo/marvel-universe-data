// p17_relationships.cypher

MATCH (c970:Character {name_en: 'Ms. Marvel (Kamala Khan)'}), (t1:Team {name_en: 'Avengers'})
MERGE (c970)-[:成员]->(t1);

MATCH (c971:Character {name_en: 'Ironheart'}), (t1:Team {name_en: 'Avengers'})
MERGE (c971)-[:成员]->(t1);

MATCH (c972:Character {name_en: 'She-Hulk'}), (t1:Team {name_en: 'Avengers'})
MERGE (c972)-[:成员]->(t1);

MATCH (c973:Character {name_en: 'Nighthawk'}), (t1:Team {name_en: 'Avengers'})
MERGE (c973)-[:成员]->(t1);
