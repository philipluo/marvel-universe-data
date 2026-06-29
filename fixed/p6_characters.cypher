// p6_characters.cypher

MERGE (c500:Character {name_en: "Mister Fantastic", name: "神奇先生", real_name: "Reed Richards", species: "人类(强化)", first_appearance: "Fantastic Four #1 (November 1961)", abilities: "天才智力, 弹性, 伸展, 科学天才"});

MERGE (c501:Character {name_en: "Invisible Woman", name: "隐形女", real_name: "Susan Storm", species: "人类(强化)", first_appearance: "Fantastic Four #1 (November 1961)", abilities: "隐形, 力场, 能量投射"});

MERGE (c502:Character {name_en: "人类 Torch", name: "霹雳火", real_name: "Johnny Storm", species: "人类(强化)", first_appearance: "Fantastic Four #1 (November 1961)", abilities: "火系能力, 飞行, 火焰操控, 无敌"});

MERGE (c503:Character {name_en: "The Thing", name: "石头人", real_name: "Ben Grimm", species: "人类(岩石形态)", first_appearance: "Fantastic Four #1 (November 1961)", abilities: "超人类力量, 岩石, 耐力, 徒手搏斗"});
