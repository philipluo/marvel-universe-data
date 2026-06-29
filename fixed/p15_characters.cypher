// p15_characters.cypher

MERGE (c950:Character {name_en: "Happy Hogan", name: "快乐·霍根", real_name: "Harold Hogan", species: "人类", first_appearance: "Tales of Suspense #42 (October 1963)", abilities: "保镖训练, 驾驶, 忠诚伙伴"});

MERGE (c951:Character {name_en: "Pepper Potts", name: "佩珀·波茨", real_name: "Virginia Potts", species: "人类", first_appearance: "Tales of Suspense #45 (January 1964)", abilities: "商业敏锐, 管理, 智力, 工业领导"});

MERGE (c952:Character {name_en: "War Machine (James Rhodes)", name: "战争机器(詹姆斯·罗德斯)", real_name: "James Rhodes", species: "人类", first_appearance: "Iron Man #118 (January 1979)", abilities: "动力装甲, 飞行, 武器系统", note: "duplicate_check"});

MERGE (c953:Character {name_en: "Ant-Man (Scott Lang)", name: "蚁人(斯科特·朗)", real_name: "Scott Lang", species: "人类", first_appearance: "Avengers #181 (March 1979)", abilities: "大小操控, 昆虫沟通", note: "duplicate_check"});

MERGE (c954:Character {name_en: "Wasp (Hope Van Dyne)", name: "黄蜂女(霍普·范·戴恩)", real_name: "Hope Van Dyne", species: "人类(强化)", first_appearance: "Tales of Suspense #44 (December 1963)", abilities: "大小操控, 生物电冲击, 飞行, 武术"});

MERGE (c955:Character {name_en: "Ant-Man (Hank Pym)", name: "蚁人(汉克·皮姆)", real_name: "Henry Pym", species: "人类(强化)", first_appearance: "Tales to Astonish #27 (January 1962)", abilities: "大小操控, 皮姆粒子, 天才智力, 昆虫控制"});
