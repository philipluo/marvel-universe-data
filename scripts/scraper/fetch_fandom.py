"""
fetch_fandom.py — Marvel Fandom Wiki 抓取 + 解析

作为 Wikipedia 的降级策略，当 Wikipedia 抓取不到时使用。
"""

import json
import re
import time
from pathlib import Path

import requests

from config import USER_AGENT, TIMEOUT, REQUESTS_DELAY, CACHE_DIR, CACHE_LIFETIME, RETRY_TIMES

FANDOM_API_BASE = "https://marvel.fandom.com/api.php"

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": USER_AGENT})
_LAST_REQUEST = 0.0


def _rate_limit():
    global _LAST_REQUEST
    now = time.time()
    since = now - _LAST_REQUEST
    if since < REQUESTS_DELAY:
        time.sleep(REQUESTS_DELAY - since)
    _LAST_REQUEST = time.time()


def _cache_get(key: str) -> dict | None:
    path = CACHE_DIR / f"fandom_{key}.json"
    if path.exists():
        import time as t
        if t.time() - path.stat().st_mtime < CACHE_LIFETIME:
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def _cache_set(key: str, data: dict):
    path = CACHE_DIR / f"fandom_{key}.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def api_query(params: dict) -> dict:
    """带缓存的 Fandom API 请求"""
    cache_key = str(params)
    cached = _cache_get(cache_key)
    if cached:
        return cached

    params.setdefault("format", "json")
    params.setdefault("action", "query")
    if "formatversion" not in params:
        params["formatversion"] = 2

    for attempt in range(RETRY_TIMES + 1):
        try:
            _rate_limit()
            resp = _SESSION.get(FANDOM_API_BASE, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            _cache_set(cache_key, data)
            return data
        except requests.RequestException as e:
            if attempt < RETRY_TIMES:
                time.sleep(2 ** attempt)
                continue
            raise


def fetch_character(title: str) -> dict | None:
    """
    从 Marvel Fandom Wiki 获取角色信息。
    作为 Wikipedia 的降级方案。
    """
    try:
        # 获取页面 wikitext
        params = {
            "prop": "revisions",
            "titles": title,
            "rvprop": "content",
            "rvslots": "main",
            "rvlimit": 1,
        }
        data = api_query(params)
        pages = data.get("query", {}).get("pages", [])
        if not pages:
            return None
        content = pages[0].get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "")
        if not content:
            return None

        return _parse_fandom_infobox(content)
    except Exception:
        return None


def _parse_fandom_infobox(wikitext: str) -> dict | None:
    """
    解析 Fandom 的 infobox（与 Wikipedia 类似但字段不同）。
    Fandom 使用 {{Infobox_character | ... }} 格式。
    """
    # 找 infobox
    m = re.search(r"\{\{Infobox_character\s*\n(.*?)\n\}\}", wikitext, re.DOTALL | re.IGNORECASE)
    if not m:
        return None

    body = m.group(1)
    props = {}

    for line in body.split("\n"):
        line = line.strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()

        # 清理 wiki 标记
        value = re.sub(r"\[\[(?:[^|]*\|)?([^\]]+)\]\]", r"\1", value)
        value = re.sub(r"\{\{[^}]+\}\}", "", value)
        value = re.sub(r"<[^>]+>", "", value)
        value = re.sub(r"'''?", "", value)
        value = re.sub(r"\s+", " ", value).strip()
        value = value.strip(",").strip()

        if not value or value.startswith("File:") or value.startswith("Image:"):
            continue

        props[key] = value

    if not props:
        return None

    return _map_fandom_props(props)


def _map_fandom_props(props: dict) -> dict:
    """Fandom 字段映射到统一 schema"""
    result = {}

    result["name_en"] = props.get("name", "") or props.get("full_name", "")
    result["name"] = ""
    result["real_name"] = props.get("real_name", "") or props.get("full_name", "")
    result["species"] = props.get("species", "") or props.get("race", "")
    result["first_appearance"] = props.get("first_appearance", "") or props.get("debut", "")
    result["abilities"] = props.get("abilities", "") or props.get("powers", "")

    team = props.get("affiliations", "") or props.get("team", "")
    if team:
        result["team_affiliations"] = team

    enemies = props.get("enemies", "") or props.get("notable_enemies", "")
    if enemies:
        result["notable_enemies"] = enemies

    return {k: v for k, v in result.items() if v}


def search_characters(search_term: str, limit: int = 20) -> list[str]:
    """在 Fandom 搜索角色"""
    params = {
        "list": "search",
        "srsearch": search_term,
        "srlimit": limit,
        "srnamespace": 0,
    }
    try:
        data = api_query(params)
        return [r.get("title", "") for r in data.get("query", {}).get("search", [])]
    except Exception:
        return []
