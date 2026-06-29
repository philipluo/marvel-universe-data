// relationships.cypher — Batch 2
// 27 条关系

MATCH (c997:Character {name_en: "Nova"}), (c400:Character {name_en: "Star-Lord"})
MERGE (c997)-[:盟友]->(c400);
MATCH (c400:Character {name_en: "Star-Lord"}), (c997:Character {name_en: "Nova"})
MERGE (c400)-[:盟友]->(c997);
MATCH (c997:Character {name_en: "Nova"}), (t7:Team {name_en: "Guardians of the Galaxy"})
MERGE (c997)-[:盟友]->(t7);
MATCH (c997:Character {name_en: "Nova"}), (c3:Character {name_en: "Thor"})
MERGE (c997)-[:盟友]->(c3);
MATCH (c3:Character {name_en: "Thor"}), (c997:Character {name_en: "Nova"})
MERGE (c3)-[:盟友]->(c997);
MATCH (c998:Character {name_en: "Adam Warlock"}), (t7:Team {name_en: "Guardians of the Galaxy"})
MERGE (c998)-[:盟友]->(t7);
MATCH (c998:Character {name_en: "Adam Warlock"}), (c300:Character {name_en: "Thanos"})
MERGE (c998)-[:盟友]->(c300);
MATCH (c300:Character {name_en: "Thanos"}), (c998:Character {name_en: "Adam Warlock"})
MERGE (c300)-[:盟友]->(c998);
MATCH (c998:Character {name_en: "Adam Warlock"}), (c901:Character {name_en: "Silver Surfer"})
MERGE (c998)-[:盟友]->(c901);
MATCH (c901:Character {name_en: "Silver Surfer"}), (c998:Character {name_en: "Adam Warlock"})
MERGE (c901)-[:盟友]->(c998);
MATCH (c999:Character {name_en: "Quasar"}), (t1:Team {name_en: "Avengers"})
MERGE (c999)-[:盟友]->(t1);
MATCH (c999:Character {name_en: "Quasar"}), (c103:Character {name_en: "Captain Marvel"})
MERGE (c999)-[:盟友]->(c103);
MATCH (c103:Character {name_en: "Captain Marvel"}), (c999:Character {name_en: "Quasar"})
MERGE (c103)-[:盟友]->(c999);
MATCH (c1000:Character {name_en: "Gladiator"}), (t1:Team {name_en: "Avengers"})
MERGE (c1000)-[:敌人]->(t1);
MATCH (t1:Team {name_en: "Avengers"}), (c1000:Character {name_en: "Gladiator"})
MERGE (t1)-[:敌人]->(c1000);
MATCH (c1000:Character {name_en: "Gladiator"}), (t5:Team {name_en: "X-Men"})
MERGE (c1000)-[:盟友]->(t5);
MATCH (c1000:Character {name_en: "Gladiator"}), (c901:Character {name_en: "Silver Surfer"})
MERGE (c1000)-[:敌人]->(c901);
MATCH (c901:Character {name_en: "Silver Surfer"}), (c1000:Character {name_en: "Gladiator"})
MERGE (c901)-[:敌人]->(c1000);
MATCH (c1000:Character {name_en: "Gladiator"}), (c902:Character {name_en: "Galactus"})
MERGE (c1000)-[:敌人]->(c902);
MATCH (c1001:Character {name_en: "Bishop"}), (t5:Team {name_en: "X-Men"})
MERGE (c1001)-[:成员]->(t5);
MATCH (c1001:Character {name_en: "Bishop"}), (c200:Character {name_en: "Professor X"})
MERGE (c1001)-[:盟友]->(c200);
MATCH (c200:Character {name_en: "Professor X"}), (c1001:Character {name_en: "Bishop"})
MERGE (c200)-[:盟友]->(c1001);
MATCH (c1001:Character {name_en: "Bishop"}), (c201:Character {name_en: "Cyclops"})
MERGE (c1001)-[:盟友]->(c201);
MATCH (c201:Character {name_en: "Cyclops"}), (c1001:Character {name_en: "Bishop"})
MERGE (c201)-[:盟友]->(c1001);
MATCH (c1005:Character {name_en: "Mister Sinister"}), (t5:Team {name_en: "X-Men"})
MERGE (c1005)-[:敌人]->(t5);
MATCH (t5:Team {name_en: "X-Men"}), (c1005:Character {name_en: "Mister Sinister"})
MERGE (t5)-[:敌人]->(c1005);
MATCH (c1005:Character {name_en: "Mister Sinister"}), (c201:Character {name_en: "Cyclops"})
MERGE (c1005)-[:敌人]->(c201);
MATCH (c201:Character {name_en: "Cyclops"}), (c1005:Character {name_en: "Mister Sinister"})
MERGE (c201)-[:敌人]->(c1005);
MATCH (c1005:Character {name_en: "Mister Sinister"}), (c204:Character {name_en: "Jean Grey"})
MERGE (c1005)-[:敌人]->(c204);
MATCH (c204:Character {name_en: "Jean Grey"}), (c1005:Character {name_en: "Mister Sinister"})
MERGE (c204)-[:敌人]->(c1005);
MATCH (c1006:Character {name_en: "Juggernaut"}), (t5:Team {name_en: "X-Men"})
MERGE (c1006)-[:敌人]->(t5);
MATCH (t5:Team {name_en: "X-Men"}), (c1006:Character {name_en: "Juggernaut"})
MERGE (t5)-[:敌人]->(c1006);
MATCH (c1006:Character {name_en: "Juggernaut"}), (c200:Character {name_en: "Professor X"})
MERGE (c1006)-[:敌人]->(c200);
MATCH (c1006:Character {name_en: "Juggernaut"}), (c200:Character {name_en: "Professor X"})
MERGE (c1006)-[:亲属]->(c200);
MATCH (c1002:Character {name_en: "Spectrum"}), (t1:Team {name_en: "Avengers"})
MERGE (c1002)-[:盟友]->(t1);
MATCH (c1002:Character {name_en: "Spectrum"}), (c103:Character {name_en: "Captain Marvel"})
MERGE (c1002)-[:盟友]->(c103);
MATCH (c103:Character {name_en: "Captain Marvel"}), (c1002:Character {name_en: "Spectrum"})
MERGE (c103)-[:盟友]->(c1002);
MATCH (c1003:Character {name_en: "White Tiger"}), (c100:Character {name_en: "Spider-Man"})
MERGE (c1003)-[:盟友]->(c100);
MATCH (c100:Character {name_en: "Spider-Man"}), (c1003:Character {name_en: "White Tiger"})
MERGE (c100)-[:盟友]->(c1003);
MATCH (c1003:Character {name_en: "White Tiger"}), (c609:Character {name_en: "Daredevil"})
MERGE (c1003)-[:盟友]->(c609);
MATCH (c609:Character {name_en: "Daredevil"}), (c1003:Character {name_en: "White Tiger"})
MERGE (c609)-[:盟友]->(c1003);
MATCH (c1004:Character {name_en: "Black Cat"}), (c100:Character {name_en: "Spider-Man"})
MERGE (c1004)-[:盟友]->(c100);
MATCH (c100:Character {name_en: "Spider-Man"}), (c1004:Character {name_en: "Black Cat"})
MERGE (c100)-[:盟友]->(c1004);
MATCH (c1004:Character {name_en: "Black Cat"}), (c607:Character {name_en: "Kingpin"})
MERGE (c1004)-[:敌人]->(c607);
MATCH (c607:Character {name_en: "Kingpin"}), (c1004:Character {name_en: "Black Cat"})
MERGE (c607)-[:敌人]->(c1004);
