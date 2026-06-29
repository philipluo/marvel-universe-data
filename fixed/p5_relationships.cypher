// p5_relationships.cypher

MATCH (c400:Character {name_en: 'Star-Lord'}), (t7:Team {name_en: 'Guardians of the Galaxy'})
MERGE (c400)-[:成员]->(t7);

MATCH (c401:Character {name_en: 'Gamora'}), (t7:Team {name_en: 'Guardians of the Galaxy'})
MERGE (c401)-[:成员]->(t7);

MATCH (c402:Character {name_en: 'Drax'}), (t7:Team {name_en: 'Guardians of the Galaxy'})
MERGE (c402)-[:成员]->(t7);

MATCH (c403:Character {name_en: 'Rocket Raccoon'}), (t7:Team {name_en: 'Guardians of the Galaxy'})
MERGE (c403)-[:成员]->(t7);

MATCH (c404:Character {name_en: 'Groot'}), (t7:Team {name_en: 'Guardians of the Galaxy'})
MERGE (c404)-[:成员]->(t7);

MATCH (c405:Character {name_en: 'Mantis'}), (t7:Team {name_en: 'Guardians of the Galaxy'})
MERGE (c405)-[:成员]->(t7);

MATCH (c406:Character {name_en: 'Nebula'}), (t7:Team {name_en: 'Guardians of the Galaxy'})
MERGE (c406)-[:成员]->(t7);

MATCH (c400:Character {name_en: 'Star-Lord'}), (c401:Character {name_en: 'Gamora'})
MERGE (c400)-[:盟友]->(c401);

MATCH (c400:Character {name_en: 'Star-Lord'}), (c401:Character {name_en: 'Gamora'})
MERGE (c401)-[:盟友]->(c400);

MATCH (c403:Character {name_en: 'Rocket Raccoon'}), (c404:Character {name_en: 'Groot'})
MERGE (c403)-[:盟友]->(c404);

MATCH (c403:Character {name_en: 'Rocket Raccoon'}), (c404:Character {name_en: 'Groot'})
MERGE (c404)-[:盟友]->(c403);

MATCH (c406:Character {name_en: 'Nebula'}), (c300:Character {name_en: 'Thanos'})
MERGE (c406)-[:敌人]->(c300);

MATCH (c406:Character {name_en: 'Nebula'}), (c300:Character {name_en: 'Thanos'})
MERGE (c300)-[:敌人]->(c406);

MATCH (c402:Character {name_en: 'Drax'}), (c300:Character {name_en: 'Thanos'})
MERGE (c402)-[:敌人]->(c300);

MATCH (c402:Character {name_en: 'Drax'}), (c300:Character {name_en: 'Thanos'})
MERGE (c300)-[:敌人]->(c402);
