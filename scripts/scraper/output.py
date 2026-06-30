"""
output.py — 爬取结果输出

将爬取 + 推断后的数据输出为 JSON 文件到 scheduled_data/crawled/。
"""

import json
from datetime import datetime

from config import CRAWLED_DIR


def save_crawled_batch(
    name: str,
    theme_str: str,
    characters: list[dict],
    relationships: list[list],
    teams: list[dict] | None = None,
) -> str:
    """
    将爬取结果保存为 scheduled_data/crawled/ 下的 JSON 文件。

    Args:
        name: 批次名称
        theme_str: 主题标识（用于文件名）
        characters: 角色列表
        relationships: 关系列表
        teams: 团队列表（可选）

    Returns: 输出文件的路径
    """
    today = datetime.now().strftime("%Y-%m-%d")
    fname = f"{today}_{theme_str}.json"
    path = CRAWLED_DIR / fname

    batch_data = {
        "name": name,
        "characters": characters,
        "relationships": relationships,
    }
    if teams:
        batch_data["teams"] = teams

    path.write_text(
        json.dumps(batch_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n📄 爬取结果已保存: {path}")
    return str(path)
