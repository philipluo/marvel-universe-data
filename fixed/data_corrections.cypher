// data_corrections.cypher
// Manually added relationships to fix known source data gaps

// Correction: Mandarin -> Iron Man (Mandarin is Iron Man's arch-nemesis)
MATCH (c923:Character {name_en: 'Mandarin'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c923)-[:敌人]->(c1);
// Correction: Ultron -> Iron Man
MATCH (c305:Character {name_en: 'Ultron'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c305)-[:敌人]->(c1);
// Correction: Doctor Doom -> Iron Man
MATCH (c302:Character {name_en: 'Doctor Doom'}), (c1:Character {name_en: 'Iron Man'})
MERGE (c302)-[:敌人]->(c1);
