// p11_relationships.cypher

MATCH (c910:Character {name_en: 'Luke Cage'}), (t10:Team {name_en: 'Heroes for Hire'})
MERGE (c910)-[:成员]->(t10);

MATCH (c911:Character {name_en: 'Iron Fist'}), (t10:Team {name_en: 'Heroes for Hire'})
MERGE (c911)-[:成员]->(t10);

MATCH (c910:Character {name_en: 'Luke Cage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c910)-[:盟友]->(c100);

MATCH (c910:Character {name_en: 'Luke Cage'}), (c100:Character {name_en: 'Spider-Man'})
MERGE (c100)-[:盟友]->(c910);

MATCH (c912:Character {name_en: 'Jessica Jones'}), (t10:Team {name_en: 'Heroes for Hire'})
MERGE (c912)-[:成员]->(t10);

MATCH (c913:Character {name_en: 'Moon Knight'}), (t10:Team {name_en: 'Heroes for Hire'})
MERGE (c913)-[:成员]->(t10);

MATCH (c914:Character {name_en: 'Shuri'}), (t1:Team {name_en: 'Avengers'})
MERGE (c914)-[:成员]->(t1);

MATCH (c915:Character {name_en: 'Okoye'}), (t1:Team {name_en: 'Avengers'})
MERGE (c915)-[:成员]->(t1);

MATCH (c914:Character {name_en: 'Shuri'}), (l10:Location {name: 'Wakanda'})
MERGE (c914)-[:来自]->(l10);

MATCH (c915:Character {name_en: 'Okoye'}), (l10:Location {name: 'Wakanda'})
MERGE (c915)-[:来自]->(l10);

MATCH (c914:Character {name_en: 'Shuri'}), (c102:Character {name_en: 'Black Panther'})
MERGE (c914)-[:亲属]->(c102);
