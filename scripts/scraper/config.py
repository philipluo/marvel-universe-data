"""
config.py — 漫威爬虫配置

主题定义、爬取策略、缓存配置。
"""

import os
from pathlib import Path

# ---------- 路径 ----------
ROOT = Path(__file__).resolve().parents[2]
CRAWLED_DIR = ROOT / "scheduled_data" / "crawled"
CACHE_DIR = ROOT / "scheduled_data" / "crawled_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 爬取策略 ----------
REQUESTS_DELAY = 2.0       # 每次请求间隔（秒）
TIMEOUT = 15               # 请求超时（秒）
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
CACHE_LIFETIME = 86400 * 7  # 缓存有效期（秒），默认 7 天
RETRY_TIMES = 1             # 失败重试次数

# ---------- 主题定义 ----------
# 每个主题包含搜索方式：
#   - wiki_list: Wikipedia 列表页面标题（从该页提取角色名）
#   - wiki_category: Wikipedia 分类名（替代 wiki_list）
#   - fandom_tag: Fandom Wiki 的标签
THEMES = {
    "street-heroes": {
        "name": "街头英雄",
        "wiki_list": "List of street-level superheroes",
        "wiki_category": "Marvel_Comics_street-level_superheroes",
        "description": "夜魔侠、惩罚者、铁拳等",
    },
    "cosmic": {
        "name": "宇宙实体",
        "wiki_category": "Marvel_Comics_cosmic_entities",
        "wiki_list": "List of Marvel Comics cosmic entities",
        "description": "Galactus、Celestials、Living Tribunal 等",
    },
    "mutants": {
        "name": "变种人",
        "wiki_category": "Marvel_Comics_mutants",
        "wiki_list": "List of Marvel Comics mutants",
        "description": "X-Men 遗漏成员、反派",
    },
    "villains": {
        "name": "反派",
        "wiki_category": "Marvel_Comics_supervillains",
        "wiki_list": "List of Marvel Comics supervillains",
        "description": "各反派角色",
    },
    "magic": {
        "name": "魔法使用者",
        "wiki_category": "Marvel_Comics_magic_users",
        "wiki_list": "List of Marvel Comics magic users",
        "description": "奇异博士相关",
    },
    "mcu-only": {
        "name": "MCU 角色",
        "wiki_category": "Marvel_Cinematic_Universe_characters",
        "wiki_list": "List of Marvel Cinematic Universe films",
        "description": "仅 MCU 已出场角色",
    },
    "avengers-expand": {
        "name": "复仇者扩展",
        "wiki_category": "Avengers_members",
        "wiki_list": "List of Avengers members",
        "description": "更多复仇者",
    },
    "xmen-expand": {
        "name": "X-Men 扩展",
        "wiki_category": "X-Men_members",
        "wiki_list": "List of X-Men members",
        "description": "更多 X-Men",
    },
    "fantastic-four": {
        "name": "神奇四侠",
        "wiki_category": "Fantastic_Four_members",
        "wiki_list": "List of Fantastic Four members",
        "description": "神奇四侠及相关角色",
    },
    "eternals": {
        "name": "永恒族",
        "wiki_category": "Eternals",
        "wiki_list": "Eternals (comics)",
        "description": "永恒族角色",
    },
}

# Wikipedia API 端点
WIKI_API_BASE = "https://en.wikipedia.org/w/api.php"
WIKI_ZH_API_BASE = "https://zh.wikipedia.org/w/api.php"
