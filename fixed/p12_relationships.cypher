// p12_relationships.cypher

MATCH (c921:Character {name_en: 'Carnage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c921)-[:敌人]->(c100);

MATCH (c921:Character {name_en: 'Carnage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c921);

MATCH (c922:Character {name_en: 'Mysterio'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c922)-[:敌人]->(c100);

MATCH (c922:Character {name_en: 'Mysterio'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c922);

MATCH (c923:Character {name_en: 'Mandarin'}), (c2:Character {name_en: 'Captain America'})
MERGE (c923)-[:敌人]->(c2);

MATCH (c923:Character {name_en: 'Mandarin'}), (c2:Character {name_en: 'Captain America'})
MERGE (c2)-[:敌人]->(c923);

MATCH (c923:Character {name_en: 'Mandarin'}), (t1:Team {name_en: 'Avengers'})
MERGE (c923)-[:敌人]->(t1);

MATCH (c923:Character {name_en: 'Mandarin'}), (t1:Team {name_en: 'Avengers'})
MERGE (t1)-[:敌人]->(c923);

MATCH (c923:Character {name_en: 'Mandarin'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c923)-[:敌人]->(c1);

MATCH (c1:Character {name_en: 'Iron Man'}), (c923:Character {name_en: 'Mandarin'})
MERGE (c1)-[:敌人]->(c923);
