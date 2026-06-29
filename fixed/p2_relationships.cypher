// p2_relationships.cypher

MATCH (c100:Character {name_en: 'Spider-Man'}), (t1:Team {name_en: 'Avengers'})
MERGE (c100)-[:成员]->(t1);

MATCH (c101:Character {name_en: 'Doctor Strange'}), (t1:Team {name_en: 'Avengers'})
MERGE (c101)-[:成员]->(t1);

MATCH (c102:Character {name_en: 'Black Panther'}), (t1:Team {name_en: 'Avengers'})
MERGE (c102)-[:成员]->(t1);

MATCH (c103:Character {name_en: 'Captain Marvel'}), (t1:Team {name_en: 'Avengers'})
MERGE (c103)-[:成员]->(t1);

MATCH (c105:Character {name_en: 'Scarlet Witch'}), (t1:Team {name_en: 'Avengers'})
MERGE (c105)-[:成员]->(t1);

MATCH (c106:Character {name_en: 'Falcon'}), (t1:Team {name_en: 'Avengers'})
MERGE (c106)-[:成员]->(t1);

MATCH (c107:Character {name_en: 'War Machine'}), (t1:Team {name_en: 'Avengers'})
MERGE (c107)-[:成员]->(t1);

MATCH (c303:Character {name_en: 'Green Goblin'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c303)-[:敌人]->(c100);

MATCH (c303:Character {name_en: 'Green Goblin'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c303);

MATCH (c306:Character {name_en: 'Venom'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c306)-[:敌人]->(c100);

MATCH (c306:Character {name_en: 'Venom'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c306);

MATCH (c5:Character {name_en: 'Black Widow'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c5)-[:盟友]->(c100);

MATCH (c5:Character {name_en: 'Black Widow'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:盟友]->(c5);

MATCH (c6:Character {name_en: 'Hawkeye'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c6)-[:盟友]->(c100);

MATCH (c6:Character {name_en: 'Hawkeye'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:盟友]->(c6);

MATCH (c102:Character {name_en: 'Black Panther'}), (l10:Location {name: 'Wakanda'})
MERGE (c102)-[:来自]->(l10);

MATCH (c101:Character {name_en: 'Doctor Strange'}), (l16:Location {name: 'Sanctum Sanctorum'})
MERGE (c101)-[:来自]->(l16);

MATCH (c100:Character {name_en: 'Spider-Man'}), (l2:Location {name: 'New York City'})
MERGE (c100)-[:来自]->(l2);

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

MATCH (c910:Character {name_en: 'Luke Cage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c910)-[:盟友]->(c100);

MATCH (c910:Character {name_en: 'Luke Cage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:盟友]->(c910);

MATCH (c914:Character {name_en: 'Shuri'}), (c102:Character {name_en: 'Black Panther'})
MERGE (c914)-[:亲属]->(c102);

MATCH (c921:Character {name_en: 'Carnage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c921)-[:敌人]->(c100);

MATCH (c921:Character {name_en: 'Carnage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c921);

MATCH (c922:Character {name_en: 'Mysterio'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c922)-[:敌人]->(c100);

MATCH (c922:Character {name_en: 'Mysterio'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:敌人]->(c922);
