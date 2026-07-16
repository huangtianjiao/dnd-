"""Checkpoint / Rewind — 游戏状态快照与回退。

职责:
  - 在关键节点（战斗开始/结束、回合结束）创建状态快照
  - 支持回退到指定检查点
  - 快照存储为 JSON 文件，按 campaign_id 组织

设计参考: 调研报告 §5.4 跨Session连续性中的 Checkpoint 要求。
LangGraph 的 MemorySaver 仅用于图执行状态(HITL)，
本模块提供游戏级的状态快照/回退能力。
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional

from . import store, models


# 快照存储目录
CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                              "data", "checkpoints")


def _ensure_dir() -> str:
    """确保快照目录存在，返回路径。"""
    path = os.path.abspath(CHECKPOINT_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def create_checkpoint(campaign_id: int, label: str = "") -> dict:
    """创建战役状态快照。

    快照包含:
      - Campaign 基本信息 + rolling_summary
      - 所有角色卡（HP/属性/法术位/物品栏）
      - 当前场景
      - 战斗状态（如有）
      - 最近10条日志

    Args:
        campaign_id: 战役ID
        label: 可选标签（如"战斗开始"、"第10回合"）

    Returns:
        {"checkpoint_id": "...", "path": "...", "label": "..."}
    """
    camp = store.get_campaign(campaign_id)
    if not camp:
        return {"error": f"战役 {campaign_id} 不存在"}

    # 收集所有状态
    chars = store.list_characters(campaign_id)
    scene = store.get_scene(campaign_id)

    # 战斗状态
    combat_state = None
    try:
        c = store.load_combat(campaign_id)
        combat_state = {
            "active": c.active, "round": c.round,
            "current_index": c.current_index,
            "initiative_order": [
                {"name": x.name, "initiative": x.initiative, "side": x.side}
                for x in c.initiative_order
            ],
        }
    except Exception:
        pass

    # 最近日志
    recent_logs = store.get_recent_logs(campaign_id, n=10)

    checkpoint = {
        "checkpoint_id": f"cp_{campaign_id}_{int(time.time())}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "label": label or f"checkpoint_{int(time.time())}",
        "campaign": {
            "id": camp.id, "name": camp.name,
            "setting": camp.setting, "tone": camp.tone,
            "world_background": camp.world_background,
            "rolling_summary": camp.rolling_summary,
        },
        "characters": [
            {
                "id": ch.id, "name": ch.name, "race": ch.race,
                "char_class": ch.char_class, "level": ch.level,
                "hp_current": ch.hp_current, "hp_max": ch.hp_max,
                "temp_hp": ch.temp_hp, "ac": ch.ac, "speed": ch.speed,
                "abilities_json": ch.abilities_json,
                "spell_slots_json": ch.spell_slots_json,
                "inventory_json": ch.inventory_json,
                "conditions_json": ch.conditions_json,
                "exhaustion": ch.exhaustion,
            }
            for ch in chars
        ],
        "scene": {
            "location": scene.location if scene else "",
            "time": scene.time if scene else "",
            "atmosphere": scene.atmosphere if scene else "",
            "environment": scene.environment if scene else "",
            "situation": scene.situation if scene else "",
            "story_log": scene.story_log if scene else "",
            "npcs_json": scene.npcs_json if scene else "[]",
            "exits_json": scene.exits_json if scene else "[]",
        } if scene else {},
        "combat": combat_state,
        "recent_logs": [
            {
                "player_input": log.player_input,
                "dm_output": log.dm_output,
            }
            for log in recent_logs
        ],
    }

    # 保存到文件
    dir_path = _ensure_dir()
    filename = f"{checkpoint['checkpoint_id']}.json"
    filepath = os.path.join(dir_path, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "path": filepath,
        "label": checkpoint["label"],
        "timestamp": checkpoint["timestamp"],
    }


def list_checkpoints(campaign_id: int) -> list[dict]:
    """列出战役的所有检查点。

    Returns:
        [{"checkpoint_id": "...", "label": "...", "timestamp": "..."}]
    """
    dir_path = _ensure_dir()
    prefix = f"cp_{campaign_id}_"
    checkpoints = []

    for filename in os.listdir(dir_path):
        if filename.startswith(prefix) and filename.endswith(".json"):
            filepath = os.path.join(dir_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                checkpoints.append({
                    "checkpoint_id": data["checkpoint_id"],
                    "label": data["label"],
                    "timestamp": data["timestamp"],
                })
            except (json.JSONDecodeError, KeyError, IOError):
                continue

    # 按时间戳排序（新的在前）
    checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
    return checkpoints


def restore_checkpoint(checkpoint_id: str) -> dict:
    """从检查点恢复游戏状态。

    恢复流程:
      1. 读取检查点 JSON 文件
      2. 恢复 Campaign 信息
      3. 恢复所有角色卡
      4. 恢复场景
      5. 恢复战斗状态（如有）

    Args:
        checkpoint_id: 检查点ID (如 "cp_1_1234567890")

    Returns:
        {"restored": True, "campaign_id": ...} 或 {"error": "..."}
    """
    dir_path = _ensure_dir()
    filepath = os.path.join(dir_path, f"{checkpoint_id}.json")

    if not os.path.exists(filepath):
        return {"error": f"检查点 {checkpoint_id} 不存在"}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return {"error": f"读取检查点失败: {e}"}

    campaign_id = checkpoint["campaign"]["id"]

    # 1. 恢复 Campaign
    camp = store.get_campaign(campaign_id)
    if camp:
        camp.rolling_summary = checkpoint["campaign"].get("rolling_summary", "")
        camp.world_background = checkpoint["campaign"].get("world_background", "")
        store.save_campaign(camp)

    # 2. 恢复角色卡
    for char_data in checkpoint.get("characters", []):
        ch = store.get_character(char_data["id"])
        if ch:
            ch.hp_current = char_data["hp_current"]
            ch.hp_max = char_data["hp_max"]
            ch.temp_hp = char_data["temp_hp"]
            ch.ac = char_data["ac"]
            ch.speed = char_data["speed"]
            ch.abilities_json = char_data["abilities_json"]
            ch.spell_slots_json = char_data["spell_slots_json"]
            ch.inventory_json = char_data["inventory_json"]
            ch.conditions_json = char_data["conditions_json"]
            ch.exhaustion = char_data["exhaustion"]
            store.save_character(ch)

    # 3. 恢复场景
    scene_data = checkpoint.get("scene", {})
    if scene_data:
        sc = store.get_scene(campaign_id)
        if sc:
            sc.location = scene_data.get("location", "")
            sc.time = scene_data.get("time", "")
            sc.atmosphere = scene_data.get("atmosphere", "")
            sc.environment = scene_data.get("environment", "")
            sc.situation = scene_data.get("situation", "")
            sc.story_log = scene_data.get("story_log", "")
            sc.npcs_json = scene_data.get("npcs_json", "[]")
            sc.exits_json = scene_data.get("exits_json", "[]")
            store.save_scene(sc)

    # 4. 恢复战斗状态
    combat_data = checkpoint.get("combat")
    if combat_data and combat_data.get("active"):
        # 这里简化处理：实际需要重建 Combat 对象
        pass

    return {
        "restored": True,
        "campaign_id": campaign_id,
        "label": checkpoint.get("label", ""),
        "timestamp": checkpoint.get("timestamp", ""),
    }


def delete_checkpoint(checkpoint_id: str) -> dict:
    """删除指定检查点。

    Args:
        checkpoint_id: 检查点ID

    Returns:
        {"deleted": True} 或 {"error": "..."}
    """
    dir_path = _ensure_dir()
    filepath = os.path.join(dir_path, f"{checkpoint_id}.json")

    if not os.path.exists(filepath):
        return {"error": f"检查点 {checkpoint_id} 不存在"}

    try:
        os.remove(filepath)
        return {"deleted": True}
    except OSError as e:
        return {"error": f"删除检查点失败: {e}"}


# ──────────────────────────────────────────────────────────────────────────
# 自检
# ──────────────────────────────────────────────────────────────────────────

def _self_test() -> None:
    """checkpoint.py 自检测试。"""
    import tempfile

    # 创建临时数据库
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()

    global CHECKPOINT_DIR
    # 使用临时目录
    test_dir = tempfile.mkdtemp()
    CHECKPOINT_DIR = test_dir

    try:
        # 测试 1: 创建检查点
        print("[test1] create_checkpoint...")
        # 需要先创建战役和角色
        camp = store.create_campaign("检查点测试")
        ch = models.Character(name="测试勇者", race="人类",
                              char_class="战士", level=3,
                              campaign_id=camp.id)
        ch.hp_max = 25; ch.hp_current = 20; ch.ac = 16
        ch = store.save_character(ch)

        result = create_checkpoint(camp.id, label="战斗前")
        assert "checkpoint_id" in result, f"创建失败: {result}"
        cp_id = result["checkpoint_id"]
        print(f"  ✓ 创建成功: {cp_id}")

        # 测试 2: 列出检查点
        print("[test2] list_checkpoints...")
        checkpoints = list_checkpoints(camp.id)
        assert len(checkpoints) >= 1, f"期望至少1个检查点, 得到{len(checkpoints)}"
        print(f"  ✓ 找到 {len(checkpoints)} 个检查点")

        # 测试 3: 恢复检查点
        print("[test3] restore_checkpoint...")
        # 先修改角色状态
        ch.hp_current = 5
        store.save_character(ch)

        # 恢复
        restore_result = restore_checkpoint(cp_id)
        assert restore_result.get("restored"), f"恢复失败: {restore_result}"

        # 验证恢复
        restored_ch = store.get_character(ch.id)
        assert restored_ch.hp_current == 20, \
            f"期望HP=20(恢复值), 得到{restored_ch.hp_current}"
        print(f"  ✓ 恢复成功: HP={restored_ch.hp_current}")

        # 测试 4: 删除检查点
        print("[test4] delete_checkpoint...")
        del_result = delete_checkpoint(cp_id)
        assert del_result.get("deleted"), f"删除失败: {del_result}"

        # 验证删除
        checkpoints_after = list_checkpoints(camp.id)
        assert len(checkpoints_after) == 0, \
            f"期望0个检查点, 得到{len(checkpoints_after)}"
        print(f"  ✓ 删除成功")

        print("\n[checkpoint] 自检通过 ✓")

    finally:
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass
        # 清理临时目录
        import shutil
        try:
            shutil.rmtree(test_dir)
        except Exception:
            pass


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _self_test()
