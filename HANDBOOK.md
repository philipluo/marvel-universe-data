# 漫威宇宙图数据库 — 使用手册

## 项目概述

本项目从公开资料收集漫威宇宙数据，生成标准 Cypher 语句导入本地 Neo4j 图数据库。

### 已收集数据规模

截至 v1.0：
- **角色**: 129（固定 106 + 定时 23）
- **团队**: 16
- **地点**: 27
- **电影**: 29
- **事件**: 19
- **物品**: 31
- **关系**: 449 条（成员/敌人/盟友/亲属/出演/来自/使用/使者）

---

## 目录结构

```
marvel-universe-data/
├── fixed/                         # 已审核的正确数据（只读）
├── scheduled_data/                # 定时抓取生成的新数据
│   ├── index.json                 # 批次状态追踪
│   ├── batch_001/                 # 每批独立目录
│   │   ├── characters.cypher
│   │   ├── teams.cypher
│   │   ├── locations.cypher
│   │   ├── movies.cypher
│   │   ├── events.cypher
│   │   ├── items.cypher
│   │   └── relationships.cypher
│   └── batch_002/
├── scripts/
│   ├── collector/                 # 数据收集器
│   │   ├── collector_helper.py    # 核心工具库
│   │   ├── data_definitions.py    # 新数据定义（按批次）
│   │   ├── run_batch.py           # 批次生成 CLI（旧）
│   │   └── run.py                 # ★ 统一入口：生成 + 双库同步
│   └── import/                    # Neo4j 导入工具
│       ├── import_all.py          # 全量导入（新库初始化）
│       ├── import_and_verify.py   # 增量导入 + 验证
│       ├── import_movie_appearances.py  # 出演关系导入
│       ├── sync_to_local.py       # ★ 单向同步到本地 Desktop
│       ├── import_neo4j.py        # CSV 导入工具
│       └── neo4j_query_llm.py     # 只读 Cypher 执行器
├── docs/
│   ├── plan/
│   │   └── v1.0_scripts_refactor_collector.md
│   └── release/
│       └── v1.0.0.md
├── REPORT.md                       # [自动生成] 人类可读的数据总表
├── .env                            # 【不提交】云端 Aura 连接配置
├── .env.local                      # 【不提交】本地 Desktop 连接配置
└── .env.example                    # 连接配置模板（无密码）
```

---

## 数据收集

### 命令参考

**新入口（推荐）：**

```bash
# 查看双库同步状态
python3 scripts/collector/run.py --status

# 生成下一批 + 同步云端 + 同步本地
python3 scripts/collector/run.py

# 不生成新批次，只重试未同步内容（可用于 cron）
python3 scripts/collector/run.py --retry

# 指定批次生成 + 同步
python3 scripts/collector/run.py --batch 3

# 强制全量重跑（幂等安全）
python3 scripts/collector/run.py --force
```

`run.py` 是推荐入口，一次性完成 生成 → 云导入 → 本地导入。每个目标不通就标记 `failed`，下次重试自动发现。

**旧入口（run_batch.py，只操作 `.env` 指向的单一目标）：**

```bash
# 查看收集进度
python3 scripts/collector/run_batch.py --status

# 列出所有定义的批次
python3 scripts/collector/run_batch.py --list-batches

# 生成下一批数据
python3 scripts/collector/run_batch.py

# 生成并导入 Neo4j（单一目标）
python3 scripts/collector/run_batch.py --import

# 仅导入已有批次（不生成新数据）
python3 scripts/collector/run_batch.py --import-only

# 仅更新 REPORT.md 总表
python3 scripts/collector/run_batch.py --report
```

每次数据收集或导入后，`REPORT.md` 会自动更新。你也可以随时用 `--report` 手动刷新。

### 输出文件格式

**角色 / 团队** — 使用 `name_en` + `name` 双字段：
```cypher
MERGE (c984:Character {name_en: "Miles Morales", name: "迈尔斯·莫拉莱斯", real_name: "Miles Morales", species: "人类(强化)", abilities: "蜘蛛感应, 隐身"});
MERGE (t17:Team {name_en: "Thunderbolts", name: "雷霆特工队", type: "反派转型团队"});
```

**地点 / 电影 / 事件 / 物品** — 使用对应标识字段：
```cypher
MERGE (l34:Location {name: "Negative Zone", type: "反物质维度"});
MERGE (m30:Movie {title: "蜘蛛侠：纵横宇宙", year: "2023"});
MERGE (e21:Event {event_name: "蜘蛛宇宙", year: "2014"});
MERGE (i215:Item {item_name: "Venom Symbiote", type: "共生体"});
```

**关系** — 使用 MATCH...MERGE 模式：
```cypher
MATCH (c984:Character {name_en: "Miles Morales"}), (t1:Team {name_en: "Avengers"})
MERGE (c984)-[:成员]->(t1);
```

关系标签统一中文：`成员`、`敌人`、`盟友`、`亲属`、`来自`、`使用`、`使者`

---

## 定时任务设置（Cron）

推荐使用 `run.py --retry`，只重试未同步内容（不会意外触发批量生成）：

```cron
# 每 4 小时重试未入库的内容（幂等安全）
0 */4 * * * cd /path/to/marvel-universe-data && python3 scripts/collector/run.py --retry >> scheduled_data/sync.log 2>&1
```

如果需要定时生成新批次（`data_definitions.py` 中定义了下游批次时）：

```cron
# 每日凌晨生成下一批并同步双库
0 3 * * * cd /path/to/marvel-universe-data && python3 scripts/collector/run.py >> scheduled_data/sync.log 2>&1
```

所有批次完成后自动输出"全部完成"并跳过，不会做无效工作。

---

## 导入新数据到 Neo4j

### 方式一：通过 run.py（推荐，双库同步）

```bash
# 生成下一批 + 同步云端 + 同步本地
python3 scripts/collector/run.py

# 仅同步已有未入库内容
python3 scripts/collector/run.py --retry

# 强制全量重跑（幂等安全）
python3 scripts/collector/run.py --force
```

### 方式二：通过 sync_to_local.py（仅同步本地）

```bash
# 查看本地待同步内容
python3 scripts/import/sync_to_local.py --status

# 同步未同步内容到本地
python3 scripts/import/sync_to_local.py
```

### 方式三：通过 run_batch.py（仅操作单一目标）

```bash
# 一次性导入所有未导入的批次
python3 scripts/collector/run_batch.py --import-only

# 生成并导入下一批
python3 scripts/collector/run_batch.py --import
```

### 方式四：手动导入

```bash
cypher-shell -a bolt://127.0.0.1:7687 -u neo4j -p neo4jneo4j -d universe -f fixed/relationships_movie_appearances.cypher
```

### 注意事项

- 导入**不会清空已有数据**（使用 MERGE 语句，幂等安全）
- 多次重复导入也不会产生重复
- 实体先导入（`characters.cypher` 等），关系后导入（`relationships.cypher`），因为关系依赖已存在的实体
- 如果关系导入报错，通常是先导入了关系文件但对应实体不存在——只需先运行实体文件再运行关系文件

---

## 添加新数据

编辑 `scripts/collector/data_definitions.py`，向 `BATCHES` 列表追加新批次：

```python
{
    "name": "My New Batch",
    "characters": [
        {
            "name_en": "NewHero",         # 英文名（唯一标识）
            "name": "新英雄",              # 中文名
            "real_name": "...",
            "species": "...",
            "first_appearance": "...",
            "abilities": "...",
        },
    ],
    "relationships": [
        # (源实体名, 源标签, 关系, 目标实体名, 目标标签, 是否双向)
        ("NewHero", "Character", "盟友", "Spider-Man", "Character", True),
        ("NewHero", "Character", "成员", "Avengers", "Team", False),
    ],
}
```

### 关系类型说明

| 关系标签 | 代码常量 | 数量 | 是否常用双向 |
|---------|---------|:---:|:-----------:|
| 出演 | `APPEARS_IN` / `出演` | 162 | 否（单向） |
| 成员 | `MEMBER_OF` / `成员` | 72 | 否（单向） |
| 敌人 | `ENEMY_OF` / `敌人` | 114 | 是（自动生成反向） |
| 盟友 | `ALLY_OF` / `盟友` | 76 | 是（自动生成反向） |
| 亲属 | `RELATIVE_OF` / `亲属` | 10 | 否 |
| 来自 | `FROM` / `来自` | 7 | 否 |
| 使用 | `USES` / `使用` | 7 | 否 |
| 使者 | `HERALD_OF` / `使者` | 1 | 否 |

---

## 故障排查

### 导入时报 "Query cannot conclude with MATCH"

原因：Cypher 语句被错误分割，MATCH 和 MERGE 分开执行。
解决：确保使用 `--import-only` 或 `--import` 方式导入（内部已正确处理多行语句）。

### 角色已存在于 Neo4j 但关系找不到

原因：关系文件先于实体文件执行。
解决：先执行实体文件，再执行关系文件。`--import` 模式会自动按正确顺序处理。

### 新增数据与已有数据重名

`run_batch.py` 会自动扫描 `fixed/` + `scheduled_data/` 中所有已有的 `name_en`，跳过重复实体。如果手动添加了重名角色，只需再次运行，系统会自动跳过。

---

## Neo4j 查询示例

```cypher
// 查看蜘蛛侠出演过的电影
MATCH (c:Character {name_en: "Spider-Man"})-[:出演]->(m:Movie)
RETURN m.title, m.year ORDER BY m.year

// 一部电影有哪些角色出演
MATCH (c:Character)-[:出演]->(m:Movie {title: "复仇者联盟：终局之战"})
RETURN c.name_en, c.name ORDER BY c.name_en

// 找出关联最多电影的角色
MATCH (c:Character)-[:出演]->(m:Movie)
RETURN c.name_en, count(m) AS movies ORDER BY movies DESC LIMIT 10

// 查看钢铁侠的盟友
MATCH (c:Character {name_en: "Iron Man"})-[:盟友]->(ally)
RETURN ally.name_en, ally.name

// 查看复仇者联盟的成员
MATCH (t:Team {name_en: "Avengers"})<-[:成员]-(c:Character)
RETURN c.name_en, c.name

// 蜘蛛侠的敌人关系网
MATCH (c:Character {name_en: "Spider-Man"})-[:敌人]-(enemy)
RETURN enemy.name_en, enemy.name

// 统计各类型节点数
MATCH (n) RETURN labels(n)[0] AS type, count(n) AS count ORDER BY count DESC

// 统计各关系类型数
MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC
```
