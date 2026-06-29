// p6_relationships.cypher

MATCH (c500:Character {name_en: 'Mister Fantastic'}), (t8:Team {name_en: 'Fantastic Four'})
MERGE (c500)-[:成员]->(t8);

MATCH (c501:Character {name_en: 'Invisible Woman'}), (t8:Team {name_en: 'Fantastic Four'})
MERGE (c501)-[:成员]->(t8);

MATCH (c502:Character {name_en: '人类 Torch'}), (t8:Team {name_en: 'Fantastic Four'})
MERGE (c502)-[:成员]->(t8);

MATCH (c503:Character {name_en: 'The Thing'}), (t8:Team {name_en: 'Fantastic Four'})
MERGE (c503)-[:成员]->(t8);

MATCH (c501:Character {name_en: 'Invisible Woman'}), (c502:Character {name_en: '人类 Torch'})
MERGE (c501)-[:亲属]->(c502);

MATCH (c500:Character {name_en: 'Mister Fantastic'}), (c501:Character {name_en: 'Invisible Woman'})
MERGE (c500)-[:亲属]->(c501);
