// p8_relationships.cypher

MATCH (c700:Character {name_en: 'Rogue'}), (t5:Team {name_en: 'X-Men'})
MERGE (c700)-[:成员]->(t5);

MATCH (c701:Character {name_en: 'Gambit'}), (t5:Team {name_en: 'X-Men'})
MERGE (c701)-[:成员]->(t5);

MATCH (c702:Character {name_en: 'Colossus'}), (t5:Team {name_en: 'X-Men'})
MERGE (c702)-[:成员]->(t5);

MATCH (c703:Character {name_en: 'Nightcrawler'}), (t5:Team {name_en: 'X-Men'})
MERGE (c703)-[:成员]->(t5);

MATCH (c704:Character {name_en: 'Psylocke'}), (t5:Team {name_en: 'X-Men'})
MERGE (c704)-[:成员]->(t5);

MATCH (c705:Character {name_en: 'Cable'}), (t5:Team {name_en: 'X-Men'})
MERGE (c705)-[:成员]->(t5);

MATCH (c707:Character {name_en: 'Emma Frost'}), (t6:Team {name_en: 'Brotherhood of Mutants'})
MERGE (c707)-[:成员]->(t6);

MATCH (c708:Character {name_en: 'Sabretooth'}), (c200:Character {name_en: 'Professor X'})
MERGE (c708)-[:敌人]->(c200);

MATCH (c708:Character {name_en: 'Sabretooth'}), (c200:Character {name_en: 'Professor X'})
MERGE (c200)-[:敌人]->(c708);

MATCH (c708:Character {name_en: 'Sabretooth'}), (c202:Character {name_en: 'Wolverine'})
MERGE (c708)-[:敌人]->(c202);

MATCH (c708:Character {name_en: 'Sabretooth'}), (c202:Character {name_en: 'Wolverine'})
MERGE (c202)-[:敌人]->(c708);

MATCH (c709:Character {name_en: 'Apocalypse'}), (t5:Team {name_en: 'X-Men'})
MERGE (c709)-[:敌人]->(t5);

MATCH (c709:Character {name_en: 'Apocalypse'}), (t5:Team {name_en: 'X-Men'})
MERGE (t5)-[:敌人]->(c709);

MATCH (c709:Character {name_en: 'Apocalypse'}), (c200:Character {name_en: 'Professor X'})
MERGE (c709)-[:敌人]->(c200);

MATCH (c709:Character {name_en: 'Apocalypse'}), (c200:Character {name_en: 'Professor X'})
MERGE (c200)-[:敌人]->(c709);

MATCH (c205:Character {name_en: 'Magneto'}), (c700:Character {name_en: 'Rogue'})
MERGE (c205)-[:敌人]->(c700);

MATCH (c205:Character {name_en: 'Magneto'}), (c700:Character {name_en: 'Rogue'})
MERGE (c700)-[:敌人]->(c205);

MATCH (c202:Character {name_en: 'Wolverine'}), (c700:Character {name_en: 'Rogue'})
MERGE (c202)-[:盟友]->(c700);

MATCH (c202:Character {name_en: 'Wolverine'}), (c700:Character {name_en: 'Rogue'})
MERGE (c700)-[:盟友]->(c202);

MATCH (c203:Character {name_en: 'Storm'}), (c700:Character {name_en: 'Rogue'})
MERGE (c203)-[:盟友]->(c700);

MATCH (c203:Character {name_en: 'Storm'}), (c700:Character {name_en: 'Rogue'})
MERGE (c700)-[:盟友]->(c203);
