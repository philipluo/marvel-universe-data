"""
relationship.py — 自动推断关系

根据角色的 team_affiliations、notable_enemies 等字段推断人物关系。
"""

import re

# 关系标签（与 collector_helper 保持一致）
REL_TYPE_MEMBER = "成员"
REL_TYPE_ENEMY = "敌人"
REL_TYPE_ALLY = "盟友"


def split_list(text: str) -> list[str]:
    """分割逗号/分号/顿号分隔的列表"""
    if not text:
        return []
    items = re.split(r"\s*[,;、]\s*", text)
    return [item.strip().lstrip("*").strip() for item in items if item.strip()]


def infer_relationships(characters: list[dict]) -> list[list]:
    """
    从角色列表推断关系。

    输入：角色 dict 列表（含 name_en, team_affiliations, notable_enemies 等）
    输出：关系列表，每项为 [src_name, src_label, rel_type, tgt_name, tgt_label, bidirectional]

    推断规则：
    1. 同一 team_affiliations 中的团队 → 成员关系
    2. team_affiliations 中同组的角色 → 盟友关系
    3. notable_enemies → 敌人关系
    """
    relationships = []
    seen = set()

    name_to_char = {c.get("name_en", ""): c for c in characters if c.get("name_en")}

    for char in characters:
        name_en = char.get("name_en", "")
        if not name_en:
            continue

        # 1. 团队归属 → 成员关系
        team_text = char.get("team_affiliations", "")
        if team_text:
            teams = split_list(team_text)
            for team in teams:
                if not team or team == name_en:
                    continue
                rel_key = (name_en, "Character", REL_TYPE_MEMBER, team, "Team")
                if rel_key not in seen:
                    seen.add(rel_key)
                    relationships.append([name_en, "Character", REL_TYPE_MEMBER, team, "Team", False])

        # 2. 敌对 → 敌人关系
        enemy_text = char.get("notable_enemies", "")
        if enemy_text:
            enemies = split_list(enemy_text)
            for enemy in enemies:
                if not enemy or enemy == name_en:
                    continue
                # 先判断 enemy 是否在角色列表中（已知角色）还是未知
                tgt_label = "Character"
                rel_key = (name_en, "Character", REL_TYPE_ENEMY, enemy, tgt_label)
                if rel_key not in seen:
                    seen.add(rel_key)
                    relationships.append([name_en, "Character", REL_TYPE_ENEMY, enemy, tgt_label, True])

    return relationships


def deduplicate_relationships(
    relationships: list[list],
    existing_entities: dict | None = None,
    new_character_names: set | None = None,
) -> list[list]:
    """
    去重关系：移除双方都不存在的。

    Args:
        relationships: 推断出的关系列表
        existing_entities: {label: {name: var}} — 从 collector_helper 获取
        new_character_names: 本批新增的角色名 set（防止误删本批角色间的关系）
    """
    if not existing_entities:
        return relationships

    new_character_names = new_character_names or set()
    result = []
    for rel in relationships:
        src_name, src_label = rel[0], rel[1]
        tgt_name, tgt_label = rel[3], rel[4]

        src_exists = existing_entities.get(src_label, {}).get(src_name)
        tgt_exists = existing_entities.get(tgt_label, {}).get(tgt_name)

        # 至少一端存在（已有或本批新增）则保留
        if src_exists or tgt_exists:
            result.append(rel)
        elif src_name in new_character_names or tgt_name in new_character_names:
            result.append(rel)
        # 两端都不存在，跳过

    return result
