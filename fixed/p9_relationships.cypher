// p9_relationships.cypher

MATCH (c800:Character {name_en: 'Winter Soldier'}), (t1:Team {name_en: 'Avengers'})
MERGE (c800)-[:成员]->(t1);

MATCH (c800:Character {name_en: 'Winter Soldier'}), (c2:Character {name_en: 'Captain America'})
MERGE (c800)-[:亲属]->(c2);

MATCH (c803:Character {name_en: 'Hercules'}), (t1:Team {name_en: 'Avengers'})
MERGE (c803)-[:盟友]->(t1);

MATCH (c803:Character {name_en: 'Hercules'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:盟友]->(c803);

MATCH (c804:Character {name_en: 'Shang-Chi'}), (t1:Team {name_en: 'Avengers'})
MERGE (c804)-[:盟友]->(t1);

MATCH (c804:Character {name_en: 'Shang-Chi'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:盟友]->(c804);

MATCH (c805:Character {name_en: 'Blade'}), (t1:Team {name_en: 'Avengers'})
MERGE (c805)-[:盟友]->(t1);

MATCH (c805:Character {name_en: 'Blade'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:盟友]->(c805);

MATCH (c806:Character {name_en: 'Ghost Rider'}), (t1:Team {name_en: 'Avengers'})
MERGE (c806)-[:盟友]->(t1);

MATCH (c806:Character {name_en: 'Ghost Rider'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:盟友]->(c806);

MATCH (c802:Character {name_en: 'Quicksilver'}), (t1:Team {name_en: 'Avengers'})
MERGE (c802)-[:成员]->(t1);
