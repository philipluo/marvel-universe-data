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
├── scheduled_data/                # 所有数据层
│   ├── curated/                   # 手工编写、审核通过的批次 (JSON)
│   │   ├── 001_spider-verse-and-more.json
│   │   └── 002_cosmic-expansion.json
│   ├── crawled/                   # 爬虫自动产出（未经审核）
│   ├── index.json                 # 批次状态追踪
│   ├── batch_001/                 # 每批独立目录（Cypher 输出）
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
│   │   ├── data_definitions.py    # 纯加载器（从 curated/ 加载 JSON）
│   │   └── run.py                 # ★ 统一入口：生成 + 双库同步
│   ├── scraper/                   # 自动爬虫模块
│   │   ├── discover.py            # CLI 入口：根据主题发现角色
│   │   ├── fetch_wiki.py          # Wikipedia 页面抓取 + infobox 解析
│   │   ├── fetch_fandom.py        # Marvel Fandom 降级源
│   │   ├── relationship.py        # 自动推断关系
│   │   ├── output.py              # 输出为 batch JSON
│   │   └── config.py              # 搜索源列表、爬取延迟等配置
│   └── import/                    # Neo4j 导入工具
│       ├── import_all.py          # 全量导入（新库初始化）
│       ├── import_and_verify.py   # 增量导入 + 验证
│       ├── import_movie_appearances.py  # 出演关系导入
│       ├── sync_to_local.py       # ★ 单向同步到本地 Desktop
│       ├── import_neo4j.py        # CSV 导入工具
│       └── neo4j_query_llm.py     # 只读 Cypher 执行器
├── docs/
│   ├── plan/
│   │   ├── v1.0_scripts_refactor_collector.md
│   │   └── v2.0_scraper_design.md
│   └── release/
│       ├── v1.0.0.md
│       └── v2.0.0.md
├── CHANGELOG.md                    # [自动生成] 数据变更日志
├── REPORT.md                       # [自动生成] 人类可读的数据总表
├── .env                            # 【不提交】云端 Aura 连接配置
├── .env.local                      # 【不提交】本地 Desktop 连接配置
└── .env.example                    # 连接配置模板（无密码）
```

---

## 数据收集

### 爬虫数据采集

系统内置自动爬虫模块 `scripts/scraper/`，可从 Wikipedia 和 Marvel Fandom Wiki 自动发现角色、抓取结构化信息、推断人物关系，输出为标准 JSON 格式供下游管道处理。

**CLI 入口：** `python3 scripts/scraper/discover.py`

```bash
# 爬取单个主题 + 自动导入数据库
python3 scripts/scraper/discover.py --theme street-heroes --count 15 --merge

# 爬取多个主题（逗号分隔），角色合并去重
python3 scripts/scraper/discover.py --theme street-heroes,cosmic,villains --count 10 --merge

# 随机 2 个主题（cron 推荐用法）
python3 scripts/scraper/discover.py --random 2 --count 10 --merge

# 仅生成 JSON 不导入，后续手动处理
python3 scripts/scraper/discover.py --theme street-heroes --count 15
python3 scripts/collector/run.py --scraped scheduled_data/crawled/2026-06-29_street-heroes.json
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `--theme` | 主题，逗号分隔多个（如 `street-heroes,cosmic`） |
| `--random N` | 从所有主题中随机选 N 个爬取（与 `--theme` 互斥） |
| `--count` | 每个主题发现多少个角色（默认 10） |
| `--merge` | 爬完后自动调用 `run.py --scraped` 导入数据库 |
| `--list-themes` | 列出所有可用主题 |

**预定义主题：** `street-heroes`、`cosmic`、`mutants`、`villains`、`magic`、`mcu-only`、`avengers-expand`、`xmen-expand`

**输出位置：** 爬取结果 JSON 保存在 `scheduled_data/crawled/YYYY-MM-DD_主题.json`

**自动导入流程：** 使用 `--merge` 时，爬虫内部自动调用 `run.py --scraped` → 生成 Cypher 文件 → 双库同步。

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

### 推荐：定时爬取新数据

每周日凌晨 3 点，随机爬取 2 个主题并自动导入。使用 `--random` 避免主题偏好，长期保持数据分布均匀。

```cron
# 每周日凌晨 3 点随机爬取 2 个主题，各 10 个角色，自动导入
0 3 * * 0 cd /path/to/marvel-universe-data && python3 scripts/scraper/discover.py --random 2 --count 10 --merge >> scheduled_data/sync.log 2>&1
```

### 备用：重试失败的同步

如果某个同步因网络等问题失败，`--retry` 只会尝试未入库的内容：

```cron
# 每 4 小时重试未入库的内容（幂等安全）
0 */4 * * * cd /path/to/marvel-universe-data && python3 scripts/collector/run.py --retry >> scheduled_data/sync.log 2>&1
```

### 注意事项

- **频率建议**：爬虫每周 1-2 次即可（Wikipedia 和 Fandom 不需要天级同步）
- **`--count` 不宜过大**：建议每主题 5-15 个，避免一次跑太久
- **`--merge` 必须加**：否则爬了不导入等于白爬
- **失败容忍**：某个页面抓取失败自动跳过，不阻塞整次运行

---

## 导入新数据到 Neo4j

### 方式一：通过 run.py（推荐，双库同步）

```bash
# 生成下一批 + 同步云端 + 同步本地
python3 scripts/collector/run.py

# 仅同步已有未入库内容
python3 scripts/collector/run.py --retry

# 导入爬虫产出的 JSON 数据
python3 scripts/collector/run.py --scraped scheduled_data/crawled/2026-06-29_street-heroes.json

# 仅生成 Cypher 不导入（预览用）
python3 scripts/collector/run.py --scraped scheduled_data/crawled/xxx.json --generate-only

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

### 方式三：手动导入

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

### 方式一：创建 JSON 批次文件（推荐）

`data_definitions.py` 已重构为纯加载器，自动扫描 `scheduled_data/curated/` 目录下的所有 JSON 文件。添加新数据只需在 `curated/` 下创建新的 JSON 文件：

```json
{
  "name": "My New Batch",
  "characters": [
    {
      "name_en": "NewHero",
      "name": "新英雄",
      "real_name": "...",
      "species": "...",
      "first_appearance": "...",
      "abilities": "..."
    }
  ],
  "relationships": [
    ["NewHero", "Character", "盟友", "Spider-Man", "Character", true],
    ["NewHero", "Character", "成员", "Avengers", "Team", false]
  ]
}
```

> **注意：** JSON 中使用数组代替 Python tuple，`true`/`false` 代替 `True`/`False`。下游通过索引访问（`rel[:5]`、`rel[5]`），行为一致。

创建文件后直接运行 `python3 scripts/collector/run.py` 即可自动加载并处理。

### 方式二：通过爬虫自动采集

```bash
python3 scripts/scraper/discover.py --theme street-heroes --count 15 --merge
```

详见「爬虫数据采集」章节。

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

`run.py` 会自动扫描 `fixed/` + `scheduled_data/` 中所有已有的 `name_en`，跳过重复实体。如果手动添加了重名角色，只需再次运行，系统会自动跳过。

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
