"""验证 senseaudio 网关 + deepseek-v4-flash 是否支持 structured output。

D1 结论（2026-07 实测）：支持。本脚本可复现该验证。
用途：决定 Director.classify_intent 是否切到 with_structured_output 主路径。

运行：python aidm/scripts/verify_structured_output.py
（需 .env 配置有效的 key）

注：当前 Director 仍走 llm.chat() + 解析失败重试（robust 且产出干净字段名，
匹配 equipment/spells/monsters 数据表）。structured output 暂缓切换——
function-calling 倾向给字段塞冗余描述（如 weapon="长剑 (longsword, 1d8...)"），
会破坏数据表查找。待 B1/B2 的查找层加"未命中→回退 equipped_weapon"兜底后再切。
详见 docs/GRAPH_DYNAMIC_REFACTOR.md 阶段D。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aidm.brain import llm  # noqa: E402


def main() -> None:
    # 1) 基本可达性
    try:
        r = llm.chat("你是测试助手。", "回复两个字:可达", temperature=0.1)
        print("[1] chat 可达:", repr(r[:60]))
    except Exception as e:  # noqa: BLE001
        print("[1] chat 失败:", type(e).__name__, str(e)[:200])
        return

    # 2) structured output
    try:
        from pydantic import BaseModel, Field

        class Intent(BaseModel):
            action_type: str = Field(description="动作类型")
            weapon: str = Field(default="", description="武器名")

        bind = llm.get_llm(temperature=0.1).with_structured_output(Intent)
        out = bind.invoke("玩家说:我用长剑攻击哥布林")
        print("[2] structured output 可用:", out)
        print("    （注意 weapon 字段可能含冗余描述，见模块 docstring）")
    except Exception as e:  # noqa: BLE001
        print("[2] structured output 不可用:", type(e).__name__, str(e)[:300])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
