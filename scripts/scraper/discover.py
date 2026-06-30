#!/usr/bin/env python3
"""
discover.py — 漫威数据爬虫 CLI 入口

从 Wikipedia / Marvel Fandom Wiki 自动发现角色，推断关系，
输出为 JSON 供 run.py --scraped 消费。

用法：
    python3 scripts/scraper/discover.py --theme street-heroes --count 15 --merge
    python3 scripts/scraper/discover.py --theme street-heroes,cosmic --count 10
    python3 scripts/scraper/discover.py --random 2 --count 10 --merge
    python3 scripts/scraper/discover.py --list-themes
"""

import argparse
import random
import subprocess
import sys
from pathlib import Path

# 确保可 import 同级模块
SCRIPTER_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTER_DIR.parents[1]
sys.path.insert(0, str(SCRIPTER_DIR))

from config import THEMES  # noqa: E402
from fetch_wiki import discover_characters  # noqa: E402
from relationship import infer_relationships  # noqa: E402
from output import save_crawled_batch  # noqa: E402

# collector_helper 用于获取已有实体列表（去重参考）
COLLECTOR_DIR = ROOT / "scripts" / "collector"
sys.path.insert(0, str(COLLECTOR_DIR))


def get_existing_entity_names() -> set:
    """获取已有实体 name_en 集合，用于预去重"""
    try:
        from collector_helper import get_all_existing_entities
        existing = get_all_existing_entities()
        char_names = set(existing.get("Character", {}).keys())
        team_names = set(existing.get("Team", {}).keys())
        return char_names | team_names
    except Exception as e:
        print(f"  ⚠️ 获取已有实体列表失败: {e}")
        return set()


def run_scraped_import(json_path: str):
    """调用 run.py --scraped 执行导入"""
    run_py = ROOT / "scripts" / "collector" / "run.py"
    result = subprocess.run(
        [sys.executable, str(run_py), "--scraped", json_path],
        capture_output=False,
    )
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="漫威数据爬虫 — 自动发现角色并导入",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  %(prog)s --theme street-heroes --count 15 --merge\n"
            "  %(prog)s --theme street-heroes,cosmic --count 10\n"
            "  %(prog)s --random 2 --count 10 --merge\n"
            "  %(prog)s --list-themes\n"
        ),
    )
    parser.add_argument("--theme", type=str, help="主题，可指定多个（逗号分隔）")
    parser.add_argument("--count", type=int, default=10, help="每个主题发现多少个角色（默认 10）")
    parser.add_argument("--list-themes", action="store_true", help="列出所有可用主题")
    parser.add_argument("--random", type=int, metavar="N", help="从所有主题中随机选 N 个")
    parser.add_argument("--merge", action="store_true", help="爬完后自动导入（调用 run.py --scraped）")

    args = parser.parse_args()

    # --list-themes
    if args.list_themes:
        print("\n可用主题:\n")
        for key, cfg in sorted(THEMES.items()):
            print(f"  {key:20s} — {cfg['description']}")
        print()
        return

    # 选择主题
    if args.theme and args.random is not None:
        print("❌ --theme 和 --random 互斥")
        sys.exit(1)

    selected_themes = []
    if args.theme:
        theme_keys = [t.strip() for t in args.theme.split(",")]
        for key in theme_keys:
            if key not in THEMES:
                print(f"❌ 未知主题: {key}（使用 --list-themes 查看可用主题）")
                sys.exit(1)
            selected_themes.append((key, THEMES[key]))
    elif args.random is not None:
        if args.random <= 0:
            print("❌ --random 需要正整数")
            sys.exit(1)
        if args.random > len(THEMES):
            print(f"⚠️  只有 {len(THEMES)} 个主题可用，将全部使用")
            args.random = len(THEMES)
        keys = random.sample(list(THEMES.keys()), args.random)
        selected_themes = [(key, THEMES[key]) for key in keys]
        print(f"\n🎲 随机选中: {', '.join(keys)}")
    else:
        print("❌ 请指定 --theme 或 --random（使用 --list-themes 查看可用主题）")
        sys.exit(1)

    # 预先获取已有实体用于去重
    existing_names = get_existing_entity_names()

    # 逐个主题爬取
    all_characters = []
    all_team_names = set()
    seen_names = set(existing_names)  # 已有 + 本批已发现的

    for theme_key, theme_config in selected_themes:
        theme_name = theme_config.get("name", theme_key)

        print(f"\n{'='*60}")
        print(f"  主题: {theme_name}（{theme_key}）")
        print(f"{'='*60}")

        characters = discover_characters(theme_config, count=args.count)

        # 去重：过滤已在库或本批已发现的
        new_chars = []
        skipped = 0
        for c in characters:
            name_en = c.get("name_en", "")
            if not name_en:
                continue
            if name_en in seen_names:
                skipped += 1
                continue
            seen_names.add(name_en)
            new_chars.append(c)

        if skipped:
            print(f"  ⏭️  跳过 {skipped} 个已有角色")

        all_characters.extend(new_chars)

    # 合并后的统计
    print(f"\n{'='*60}")
    print(f"  合并结果: 共 {len(all_characters)} 个新角色")
    print(f"{'='*60}")

    if not all_characters:
        print("📭 没有发现新角色")
        return

    # 推断关系
    print("\n🔗 推断关系...")
    relationships = infer_relationships(all_characters)
    print(f"  📊 推断出 {len(relationships)} 条关系")

    # 生成批次名
    theme_strs = [k.replace("-", "-") for k, _ in selected_themes]
    theme_slug = "-".join(theme_strs) if len(theme_strs) <= 3 else f"random-{len(theme_strs)}"
    batch_name = " & ".join(cfg.get("name", k) for k, cfg in selected_themes[:3])
    if len(selected_themes) > 3:
        batch_name += f" 等 {len(selected_themes)} 个主题"

    # 保存 JSON
    json_path = save_crawled_batch(
        name=batch_name,
        theme_str=theme_slug,
        characters=all_characters,
        relationships=relationships,
    )

    # --merge
    if args.merge:
        print(f"\n🔄 自动导入...")
        run_scraped_import(json_path)

    print("\n✅ 完成")


if __name__ == "__main__":
    main()
