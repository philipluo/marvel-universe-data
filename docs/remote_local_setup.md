# Remote / Local 双机协作说明

> 项目需要在多台电脑上运行：Remote 主力机（只有云端 Neo4j）+ Local 偶尔使用机（有云端 + 本地 Desktop）。

---

## 总结一句话

当前架构**不需要改代码**。Remote 不创建 `.env.local`，Local 照常配好两个文件，`index.json` 通过 git 传递同步状态，全自动适配。

---

## 每台机器的配置

### Remote 电脑（主力，只有云）

```
项目目录/
├── .env          → 配云端 Aura（必须）
├── .env.local    → ❌ 不要创建这个文件
└── ...其他文件（git clone/pull）
```

`run.py` 看到 `.env.local` 不存在，会自动打印 `⏭️ 本地: .env.local 不存在` 并跳过本地同步，不报错。

### Local 电脑（有本地 Desktop）

```
项目目录/
├── .env          → 配云端 Aura（必须）
├── .env.local    → 配本地 bolt://127.0.0.1:7687
└── ...其他文件（git clone/pull）
```

两台机器的 `.env.*` 都是 `.gitignore` 保护的，各配各的，互不干扰。

---

## import_log 是跨机同步的"信使"

`scheduled_data/index.json` 是 git 跟踪的文件，它的 `import_log` 字段记录了每个批次在 cloud 和 local 两个目标的入库状态（`ok` / `pending` / `failed`）。跨机同步时，这个文件自动传递同步状态：

### Remote 生成 Batch 3 并推送到云

```
Remote: run.py
  → 生成 Batch 3 数据文件（fixed + 关系）
  → import_log:
      cloud.batch.3 = "pending"
      local.batch.3 = "pending"   ← Remote 没有 .env.local，这里会留着
  → 同步云端成功 → cloud.batch.3 = "ok"
  → 本地跳过 → local.batch.3 仍是 "pending"
  → 写入 index.json
  → git add + commit + push
```

### Local 拉取并同步到本地 Desktop

```
Local: git pull
  → 看到 import_log 里 local.batch.3 = "pending"
  → run.py --retry
  → 同步本地 Desktop → local.batch.3 = "ok"
  → 同步云端（幂等，无重复）
  → git add scheduled_data/index.json + commit + push
```

**关键：** 所有 `.cypher` 数据文件也在 git 中，两边的数据内容永远一致。`index.json` 只记录"是否已入库"的状态。

---

## 日常操作流程

### Remote 电脑（主力，每天用）

```bash
# 生成新批次 + 同步云
python3 scripts/collector/run.py

# 或者 cron 定时重试
python3 scripts/collector/run.py --retry

# 提交到 git
git add -A
git commit -m "marvel: batch 3 update"
git push
```

### Local 电脑（偶尔用）

```bash
# 拉取 Remote 的最新数据
git pull

# 同步到本地 Desktop
python3 scripts/collector/run.py --retry

# 把 index.json 的状态更新提交回去
git add scheduled_data/index.json
git commit -m "sync: local batch 3"
git push
```

Local 不需要每次都用完就 push，可以攒几次一起提交。

---

## FAQ

### 两台电脑的 index.json 会不会冲突？

可能。如果 Remote 和 Local 都生成新的 `import_log` 字段提交到同一行，git pull 会报合并冲突。

**但现实中不会发生：** Remote 是主力机，只有 Remote 能生成新批次（`run.py` 无参数）。Local 只跑 `--retry`，只修改 `import_log.local.*` 的字段值。两者的改动不重叠，git 能自动合并。

唯一可能冲突的情况：两台机器同时修改 `import_log.cloud.batch.X` 和 `import_log.local.batch.X`——不会发生，因为 Remote 不写 local 字段，Local 只有在 git pull 之后才跑。

### Remote 偶尔也要用 `--retry` 怎么办？

Rest Remote 的 `.env.local` 不存在，跑 `--retry` 时同样会跳过本地同步，只重试云端的 pending/failed 内容，完全兼容。

### 如果 Remote 误创建了 `.env.local`？

`run.py` 会尝试连接本地 Desktop 并失败，打印 `❌ 本地: 无法连接`，把 local 标记为 `failed`。不影响云端同步，只是多一行日志。删除 `.env.local` 即可恢复跳过行为。
