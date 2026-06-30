"""
fetch_wiki.py — Wikipedia 页面抓取 + infobox 解析

通过 MediaWiki API 获取页面 wikitext 并解析 infobox 结构字段。
"""

import json
import re
import time
from pathlib import Path

import requests

from config import (
    WIKI_API_BASE, WIKI_ZH_API_BASE, USER_AGENT, TIMEOUT,
    REQUESTS_DELAY, CACHE_DIR, CACHE_LIFETIME, RETRY_TIMES,
)

# ---------- Session ----------
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": USER_AGENT})
_LAST_REQUEST = 0.0


def _rate_limit():
    """控制请求频率"""
    global _LAST_REQUEST
    now = time.time()
    since = now - _LAST_REQUEST
    if since < REQUESTS_DELAY:
        time.sleep(REQUESTS_DELAY - since)
    _LAST_REQUEST = time.time()


def _cache_path(key: str) -> Path:
    """缓存文件路径"""
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", key)
    return CACHE_DIR / f"wiki_{safe}.json"


def _cached_request(url: str, params: dict, cache_key: str | None = None) -> dict:
    """带缓存的 MediaWiki API 请求"""
    effective_key = cache_key or url + json.dumps(params, sort_keys=True)
    cache_file = _cache_path(effective_key)

    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_LIFETIME:
            return json.loads(cache_file.read_text(encoding="utf-8"))

    for attempt in range(RETRY_TIMES + 1):
        try:
            _rate_limit()
            resp = _SESSION.get(url, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return data
        except requests.RequestException as e:
            if attempt < RETRY_TIMES:
                time.sleep(2 ** attempt)
                continue
            raise


def api_query(params: dict, api_base: str = WIKI_API_BASE, cache_key: str | None = None) -> dict:
    """通用 Wikipedia API 查询"""
    params.setdefault("format", "json")
    params.setdefault("action", "query")
    if "formatversion" not in params:
        params["formatversion"] = 2
    return _cached_request(api_base, params, cache_key=cache_key)


# ---------- 从列表/分类页发现角色 ----------

def get_characters_from_category(category: str) -> list[str]:
    """
    通过 categorymembers API 获取分类下所有页面标题。
    只返回主命名空间（ns=0）的页面。
    """
    titles = []
    cmcontinue = None

    while True:
        params = {
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": "max",
            "cmtype": "page",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        data = api_query(params, cache_key=f"cat_{category}_{cmcontinue or '0'}")
        pages = data.get("query", {}).get("categorymembers", [])
        for p in pages:
            title = p.get("title", "")
            if title and ":" not in title:  # 跳过命名空间页（如 File:...）
                titles.append(title)

        cont = data.get("continue", {})
        cmcontinue = cont.get("cmcontinue")
        if not cmcontinue:
            break

    return titles


def get_characters_from_list(list_title: str) -> list[str]:
    """
    通过 links API 获取列表页中链接到的页面标题。
    """
    titles = []
    plcontinue = None

    while True:
        params = {
            "prop": "links",
            "titles": list_title,
            "pllimit": "max",
            "plnamespace": 0,
        }
        if plcontinue:
            params["plcontinue"] = plcontinue

        data = api_query(params, cache_key=f"links_{list_title}_{plcontinue or '0'}")
        pages = data.get("query", {}).get("pages", [])
        for page in pages:
            links = page.get("links", [])
            for link in links:
                titles.append(link.get("title", ""))

        cont = data.get("continue", {})
        plcontinue = cont.get("plcontinue")
        if not plcontinue:
            break

    return titles


def search_characters(search_term: str, limit: int = 50) -> list[str]:
    """
    通过 search API 搜索角色。
    """
    params = {
        "list": "search",
        "srsearch": search_term,
        "srlimit": limit,
        "srnamespace": 0,
    }
    data = api_query(params, cache_key=f"search_{search_term}_{limit}")
    return [r.get("title", "") for r in data.get("query", {}).get("search", [])]


# ---------- 解析 infobox ----------

def _parse_infobox_from_wikitext(wikitext: str) -> dict:
    """
    从 wikitext 中解析 infobox 参数。

    Wikipedia infobox 的 wikitext 格式：
    {{Infobox character
    | name = Iron Man
    | real_name = Tony Stark
    ...
    }}

    返回 {参数名: 值} 字典，清理 Markdown/wiki 标记。
    """
    props = {}

    # 查找 infobox 模板（嵌套大括号最佳近似）
    # 策略：找到 {{Infobox... 然后通过 {} 计数找到配对的 }}
    depth = 0
    infobox_start = -1
    infobox_end = -1

    # 找所有 {{Infobox 开头
    for m in re.finditer(r"\{\{Infobox", wikitext):
        start = m.start()
        depth = 0
        i = start
        while i < len(wikitext):
            ch = wikitext[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    infobox_end = i + 1
                    break
            i += 1
        if infobox_end > 0:
            infobox_text = wikitext[start:infobox_end]
            break

    if not infobox_text:
        return props

    # 逐行解析参数
    for line in infobox_text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        line = line[1:].strip()
        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        # 清理 wiki 标记
        value = re.sub(r"\[\[(?:[^|]*\|)?([^\]]+)\]\]", r"\1", value)  # [[link|text]] → text
        value = re.sub(r"\{\{[^}]+\}\}", "", value)  # {{template}} → 删除
        value = re.sub(r"<[^>]+>", "", value)  # <ref>...</ref> → 删除
        value = re.sub(r"'''?", "", value)  # 加粗标记
        value = re.sub(r"\s+", " ", value).strip()
        value = re.sub(r"&amp;", "&", value)
        value = re.sub(r"&lt;", "<", value)
        value = re.sub(r"&gt;", ">", value)
        value = value.strip(",").strip()

        # 跳过空值、图片、引用
        if not value or value.startswith("File:") or value.startswith("Image:"):
            continue

        key_normalized = key.lower().replace(" ", "_").replace("-", "_")
        props[key_normalized] = value

    return props


def _map_wiki_props(infobox: dict, lang: str = "en") -> dict:
    """
    将 Wikipedia infobox 字段映射到统一 schema。

    映射表：
    | Wikipedia 字段（英文） | 输出字段 |
    |----|------|
    | name / aliases → name (英文名)
    | chinese_name / also_known_as → name (中文名)
    | real_name → real_name
    | species / race → species
    | first_appearance → first_appearance
    | abilities / powers → abilities
    | affiliations / team → team_affiliations
    | enemies → notable_enemies
    """
    result = {}

    # 名字
    if lang == "zh":
        cn = infobox.get("中文名") or infobox.get("译名") or infobox.get("name", "")
        result["name"] = cn.strip() if cn else ""
        en = infobox.get("英文名", "")
        result["name_en"] = en
    else:
        result["name_en"] = infobox.get("name", "") or infobox.get("aliases", "")
        result["name"] = ""

    # 真实姓名
    real_name = (
        infobox.get("real_name") or infobox.get("full_name")
        or infobox.get("真实姓名") or infobox.get("本名") or ""
    )
    result["real_name"] = real_name

    # 物种
    species = (
        infobox.get("species") or infobox.get("race")
        or infobox.get("种类") or infobox.get("物种") or ""
    )
    result["species"] = species

    # 首次出场
    fa = (
        infobox.get("first_appearance") or infobox.get("first_issue")
        or infobox.get("初次出现") or ""
    )
    result["first_appearance"] = fa

    # 能力
    abilities = (
        infobox.get("abilities") or infobox.get("powers")
        or infobox.get("能力") or ""
    )
    result["abilities"] = abilities

    # 团队（用于关系推断）
    team = (
        infobox.get("affiliations") or infobox.get("team")
        or infobox.get("team_affiliations") or infobox.get("所属团队")
        or ""
    )
    if team:
        result["team_affiliations"] = team

    # 敌人
    enemies = (
        infobox.get("enemies") or infobox.get("notable_enemies")
        or infobox.get("主要敌人") or ""
    )
    if enemies:
        result["notable_enemies"] = enemies

    # 过滤空值
    return {k: v for k, v in result.items() if v}


def fetch_character_infobox(title: str) -> dict:
    """
    获取一个 Wikipedia 页面的 infobox 数据。

    先用英文 Wikipedia，然后用中文 Wikipedia 补中文名。
    """
    # 1. 英文版
    props_en = _fetch_single_infobox(title, WIKI_API_BASE, "en")

    # 2. 中文版补中文名
    props_cn = _fetch_single_infobox(title, WIKI_ZH_API_BASE, "zh")
    if props_cn.get("name"):
        props_en["name"] = props_cn["name"]

    return props_en


def _fetch_single_infobox(title: str, api_base: str, lang: str) -> dict:
    """
    从单个 Wikipedia 获取页面的 infobox。
    """
    params = {
        "prop": "revisions",
        "titles": title,
        "rvprop": "content",
        "rvslots": "main",
        "rvlimit": 1,
    }
    cache_key = f"wikitext_{lang}_{title}"

    try:
        data = api_query(params, api_base=api_base, cache_key=cache_key)
        pages = data.get("query", {}).get("pages", [])
        if not pages:
            return {}
        content = pages[0].get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "")
        if not content:
            return {}
        infobox = _parse_infobox_from_wikitext(content)
        return _map_wiki_props(infobox, lang=lang)
    except Exception:
        return {}


# ---------- 主题发现 ----------

def discover_characters(theme_config: dict, count: int = 10) -> list[dict]:
    """
    根据主题配置发现角色。

    Args:
        theme_config: config.py THEMES 中的主题配置
        count: 需要获取多少个角色

    Returns: [{"name": ..., "name_en": ..., ...}, ...]
    """
    # 1. 获取候选角色名列表
    candidates = []
    wiki_list = theme_config.get("wiki_list")
    wiki_category = theme_config.get("wiki_category")

    if wiki_category:
        try:
            candidates = get_characters_from_category(wiki_category)
            if candidates:
                print(f"  📋 从分类 {wiki_category} 发现 {len(candidates)} 个页面")
        except Exception as e:
            print(f"  ⚠️ 分类获取失败: {e}")

    if not candidates and wiki_list:
        try:
            candidates = get_characters_from_list(wiki_list)
            if candidates:
                print(f"  📋 从列表 {wiki_list} 发现 {len(candidates)} 个链接")
        except Exception as e:
            print(f"  ⚠️ 列表获取失败: {e}")

    if not candidates:
        # 兜底：搜索
        theme_name = theme_config.get("name", "")
        search_term = f"Marvel Comics {theme_name} character"
        try:
            candidates = search_characters(search_term, limit=count * 2)
            if candidates:
                print(f"  📋 从搜索 '{search_term}' 发现 {len(candidates)} 个结果")
        except Exception as e:
            print(f"  ⚠️ 搜索失败: {e}")

    if not candidates:
        print("  ⚠️ 未找到任何候选页面")
        return []

    # 2. 限制数量并去重
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    # 取前 count 个（或者更多，因为一些可能抓取失败）
    targets = unique[:max(count * 2, 20)]

    # 3. 逐个抓取 infobox
    characters = []
    errors = 0
    for i, title in enumerate(targets):
        if len(characters) >= count:
            break

        print(f"  🔍 ({i+1}/{len(targets)}) 抓取: {title}", end="")
        try:
            props = fetch_character_infobox(title)
            if props.get("name_en"):
                characters.append(props)
                print(f" → ✅ {props.get('name', '')}")
            else:
                print(f" → ⏭️  infobox 未识别为角色")
        except Exception as e:
            errors += 1
            print(f" → ❌ {e}")

    # 4. 如果抓取成功的少于 count，从 targets 补充
    if len(characters) < count:
        remaining = [t for t in targets if t not in {c.get("name_en", "") for c in characters}]
        for title in remaining:
            if len(characters) >= count:
                break
            try:
                props = fetch_character_infobox(title)
                if props.get("name_en"):
                    characters.append(props)
            except Exception:
                pass

    print(f"\n  📊 共获取 {len(characters)} 个角色（{errors} 个失败）")
    return characters
