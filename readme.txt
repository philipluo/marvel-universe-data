第一步：创建修改版任务指令 (marvel_cypher_task.txt)
在你的工作目录下创建 marvel_cypher_task.txt。这个 Prompt 的核心是让 Agent 充当一个数据ETL（抽取-转换-加载）工具，只输出语法严格的 Cypher 语句文件。

你现在是一个大模型长任务测试专家。我们需要开启一个长期的、免人类干预的漫威宇宙（Marvel Universe）知识库搜集任务，并将数据转化为可直接导入 Neo4j 的 Cypher 语句。

【任务核心目标】
自主通过浏览器搜索、抓取“漫威宇宙”的核心公开信息。你不需要实际连接 Neo4j 数据库，而是将所有搜集到的实体和关系，转化为标准的 Cypher 语句，并以追加（Append）的方式写入本地的 `.cypher` 文件中。

【输出文件与格式规范】
1. 根目录：在当前目录下创建 `marvel_graph_data` 文件夹。
2. 核心图数据文件：所有转换后的 Cypher 语句全部写入并保存在 `marvel_graph_data/import_data.cypher` 文件中。
3. Cypher 语法约束（极其重要）：
   - 节点和关系必须使用 `MERGE` 语句，严禁使用 `CREATE`，以防后续重复导入时产生冗余节点。
   - 示例：
     MERGE (c1:Character {name: "Iron Man", real_name: "Tony Stark", abilities: "Power Armor"})
     MERGE (t1:Team {name: "Avengers"})
     MERGE (c1)-[:MEMBER_OF]->(t1);
   - 属性值中的特殊字符（如单引号/双引号）必须进行转义处理（如 `\'`），防止导入时 Cypher 语法报错。

【状态检查与断点续传】
每次启动时，你必须先读取 `marvel_graph_data/import_data.cypher` 文件（如果已存在），分析里面已经搜集了哪些英雄或事件。本次运行只做增量搜集，绝不重复生成已存在的实体。

【自我审计与遥测（核心测试项）】
在 `marvel_graph_data` 目录下创建一个名为 `telemetry_log.csv` 的文件。
每次你完成一个网页的抓取，并向 `.cypher` 文件成功追加写入数据后，必须向 `telemetry_log.csv` 追加一行记录：
[时间戳], [当前操作/子任务名称], [本次请求Prompt_Tokens], [本次请求Completion_Tokens], [估计当前Context总长度], [当前.cypher文件行数]
以此来监控你的 Token 消耗趋势、上下文膨胀情况以及代码产出效率。

【免干预执行约束】
- 你必须完全独立做出决策。若遇到网页反爬或信息缺失，自主寻找备用维基网站（如 Marvel Database Wiki 等），不向人类提问。
- 采用温和抓取策略：每连续抓取或分析 1-2 个页面，自主进行 30-60 秒的延迟（Sleep），防止被网站封禁。
- 执行完毕后，请在终端输出“TASK_BATCH_COMPLETED”，然后自主安全退出。

现在，请开始你的第一步：检查当前目录，规划本次运行的增量搜集路线图。

第二步：编写后台自动化脚本 (run_hermes.sh)
由于不需要实际连接网络数据库，Hermes 只需要开启 web 工具集来爬取网页即可。它会利用自身的原生文件写入能力或本地 Python 来生成文件。
第三步：挂在后台不间断运行
执行以下命令，让它在后台完全自主地跑起来：
运行中与后续导入怎么做？
过程观察：
你可以随时输入 tail -f marvel_graph_data/telemetry_log.csv。在这个 CSV 中，最后一列就是 .cypher 文件的总行数。如果这个数字随着时间在稳定上升，同时前几列的 Token 消耗也在合理膨胀，说明你的压力测试进行得非常完美！
成果检查：
可以随时用 cat marvel_graph_data/import_data.cypher 来看一眼它写出来的代码是不是标准合规的 Cypher 语句。


