// p7_relationships.cypher

MATCH (c600:Character {name_en: 'Mary Jane Watson'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c600)-[:亲属]->(c100);

MATCH (c601:Character {name_en: 'J. Jonah Jameson'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c601)-[:敌人]->(c100);

MATCH (c601:Character {name_en: 'J. Jonah Jameson'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c601);

MATCH (c602:Character {name_en: 'Doc Ock'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c602)-[:敌人]->(c100);

MATCH (c602:Character {name_en: 'Doc Ock'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c602);

MATCH (c603:Character {name_en: 'Sandman'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c603)-[:敌人]->(c100);

MATCH (c603:Character {name_en: 'Sandman'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c603);

MATCH (c604:Character {name_en: 'Electro'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c604)-[:敌人]->(c100);

MATCH (c604:Character {name_en: 'Electro'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c604);

MATCH (c605:Character {name_en: 'Lizard'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c605)-[:敌人]->(c100);

MATCH (c605:Character {name_en: 'Lizard'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c605);

MATCH (c606:Character {name_en: 'Vulture'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c606)-[:敌人]->(c100);

MATCH (c606:Character {name_en: 'Vulture'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c606);

MATCH (c607:Character {name_en: 'Kingpin'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c607)-[:敌人]->(c100);

MATCH (c607:Character {name_en: 'Kingpin'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c607);

MATCH (c608:Character {name_en: 'Punisher'}), (c609:Character {name_en: 'Daredevil'})
MERGE (c608)-[:敌人]->(c609);

MATCH (c608:Character {name_en: 'Punisher'}), (c609:Character {name_en: 'Daredevil'})
MERGE (c609)-[:敌人]->(c608);

MATCH (c609:Character {name_en: 'Daredevil'}), (t9:Team {name_en: 'Defenders'})
MERGE (c609)-[:成员]->(t9);

MATCH (c610:Character {name_en: 'Elektra'}), (c609:Character {name_en: 'Daredevil'})
MERGE (c610)-[:盟友]->(c609);

MATCH (c610:Character {name_en: 'Elektra'}), (c609:Character {name_en: 'Daredevil'})
MERGE (c609)-[:盟友]->(c610);
