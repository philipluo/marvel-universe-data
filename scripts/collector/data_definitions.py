"""
data_definitions.py — 批次数据纯加载器

从 scheduled_data/curated/*.json 中加载 BATCHES 列表。
所有手工编写或爬虫产生的数据集均为 JSON 文件，不再硬编码 Python。
"""

import json
from pathlib import Path

BATCHES_DIR = Path(__file__).resolve().parents[2] / "scheduled_data" / "curated"


def _load_batches():
    if not BATCHES_DIR.exists():
        return []
    batches = []
    for fpath in sorted(BATCHES_DIR.glob("*.json")):
        if fpath.name == "manifest.txt":
            continue
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            batches.append(data)
        except json.JSONDecodeError as e:
            print(f"⚠️  跳过 {fpath.name}: JSON 解析失败 — {e}")
    return batches


BATCHES = _load_batches()
