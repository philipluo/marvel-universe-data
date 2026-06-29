// p10_relationships.cypher

MATCH (c901:Character {name_en: 'Silver Surfer'}), (c902:Character {name_en: 'Galactus'})
MERGE (c901)-[:使者]->(c902);

MATCH (c900:Character {name_en: 'Captain Universe'}), (c300:Character {name_en: 'Thanos'})
MERGE (c900)-[:敌人]->(c300);

MATCH (c900:Character {name_en: 'Captain Universe'}), (c300:Character {name_en: 'Thanos'})
MERGE (c300)-[:敌人]->(c900);
