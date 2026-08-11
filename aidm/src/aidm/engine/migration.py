"""内容定义版本追踪与存档迁移。

设计原则：
  - DefinitionRevision 追踪每个内容定义（法术/怪物/特性等）的版本。
  - MigrationPlan 描述从旧版本到新版本的迁移步骤。
  - 存档加载时对比 revision，自动执行迁移保证兼容性。

规则依据: DATA-003 Definition Revision
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class DefinitionRevision:
    """内容定义的版本追踪。

    每个内容定义（法术/怪物/特性等）都有一个 revision 标识。
    当定义发生变化时，递增 revision 并记录 changes。
    存档加载时通过 revision 对比判断是否需要迁移。

    属性:
        content_id: 内容唯一标识（如 "spell.fireball" / "monster.goblin"）
        revision: 当前版本号（语义化版本 "major.minor"）
        previous_revision: 上一个版本号（None 表示初始版本）
        changes: 本次版本变更的描述列表
    """

    content_id: str
    revision: str = "1.0"
    previous_revision: Optional[str] = None
    changes: List[str] = field(default_factory=list)

    def bump(self, change_description: str = "") -> None:
        """递增版本号（minor 版本+1），记录变更。"""
        parts = self.revision.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        self.previous_revision = self.revision
        self.revision = f"{major}.{minor + 1}"
        if change_description:
            self.changes.append(f"{self.previous_revision} → {self.revision}: {change_description}")

    def bump_major(self, change_description: str = "") -> None:
        """递增主版本号（major+1, minor 归零），记录变更。"""
        parts = self.revision.split(".")
        major = int(parts[0])
        self.previous_revision = self.revision
        self.revision = f"{major + 1}.0"
        if change_description:
            self.changes.append(f"{self.previous_revision} → {self.revision}: {change_description}")


@dataclass
class MigrationStep:
    """单个迁移步骤。

    属性:
        description: 步骤描述
        field_path: 要修改的字段路径（如 "spell_slots.1"）
        operation: 操作类型（"rename" / "set_default" / "transform" / "remove"）
        old_value: 旧值（用于 rename/remove 匹配）
        new_value: 新值（用于 set_default/rename）
        transform_fn: 自定义转换函数（operation="transform" 时使用）
    """

    description: str = ""
    field_path: str = ""
    operation: str = "set_default"  # rename / set_default / transform / remove
    old_value: Any = None
    new_value: Any = None
    transform_fn: Optional[Callable[[Any], Any]] = None


@dataclass
class MigrationPlan:
    """存档迁移计划。

    描述从 from_revision 到 to_revision 的迁移步骤序列。
    存档加载时，如果存档的 revision 低于当前定义的 revision，
    则按 MigrationPlan 的步骤依次执行迁移。

    属性:
        from_revision: 起始版本号
        to_revision: 目标版本号
        steps: 迁移步骤列表
        content_id: 关联的内容定义 ID
    """

    from_revision: str
    to_revision: str
    steps: List[MigrationStep] = field(default_factory=list)
    content_id: str = ""

    def validate(self) -> bool:
        """校验迁移计划是否合法。

        检查:
          - from_revision != to_revision
          - 每个步骤的 operation 合法
          - transform 步骤必须有 transform_fn

        Returns:
            是否合法
        """
        if self.from_revision == self.to_revision:
            return False
        valid_ops = {"rename", "set_default", "transform", "remove"}
        for step in self.steps:
            if step.operation not in valid_ops:
                return False
            if step.operation == "transform" and step.transform_fn is None:
                return False
        return True

    def execute(self, save_data: dict) -> dict:
        """执行迁移，返回迁移后的存档数据。

        按步骤依次执行：
          - rename: 将字段从 old_value（字段名）重命名为 new_value（字段名）
          - set_default: 如果字段不存在，设置为 new_value
          - transform: 用 transform_fn 转换字段值
          - remove: 删除字段

        Args:
            save_data: 存档数据字典

        Returns:
            迁移后的存档数据（原地修改并返回）

        Raises:
            ValueError: 迁移计划未通过校验
        """
        if not self.validate():
            raise ValueError(
                f"迁移计划无效: {self.from_revision} → {self.to_revision}"
            )

        for step in self.steps:
            data = save_data
            # 支持嵌套字段路径（如 "spell_slots.1"）
            path_parts = step.field_path.split(".") if step.field_path else []
            parent = data
            for part in path_parts[:-1]:
                if isinstance(parent, dict):
                    parent = parent.setdefault(part, {})
                elif isinstance(parent, list):
                    idx = int(part)
                    while len(parent) <= idx:
                        parent.append({})
                    parent = parent[idx]

            key = path_parts[-1] if path_parts else ""

            if step.operation == "rename" and key:
                # 重命名字段
                if key in parent:
                    parent[str(step.new_value)] = parent.pop(key)

            elif step.operation == "set_default" and key:
                # 设置默认值（仅当字段不存在时）
                if key not in parent:
                    parent[key] = step.new_value

            elif step.operation == "transform" and key:
                # 自定义转换
                if key in parent and step.transform_fn is not None:
                    parent[key] = step.transform_fn(parent[key])

            elif step.operation == "remove" and key:
                # 删除字段
                parent.pop(key, None)

        return save_data


class MigrationRegistry:
    """迁移注册表 — 管理所有内容定义的迁移计划。

    使用方式:
        registry = MigrationRegistry()
        registry.register_plan(MigrationPlan(
            from_revision="1.0", to_revision="1.1",
            content_id="spell.fireball",
            steps=[MigrationStep(
                description="火球术伤害骰从 6d6 改为 8d6",
                field_path="damage_dice",
                operation="set_default",
                new_value="8d6",
            )],
        ))
        # 加载存档时
        migrated = registry.migrate("spell.fireball", "1.0", save_data)
    """

    def __init__(self) -> None:
        self._plans: Dict[str, List[MigrationPlan]] = {}

    def register_plan(self, plan: MigrationPlan) -> None:
        """注册一个迁移计划。"""
        key = plan.content_id
        if key not in self._plans:
            self._plans[key] = []
        self._plans[key].append(plan)

    def get_plan(self, content_id: str, from_revision: str) -> Optional[MigrationPlan]:
        """获取指定内容从指定版本开始的迁移计划。"""
        plans = self._plans.get(content_id, [])
        for plan in plans:
            if plan.from_revision == from_revision:
                return plan
        return None

    def migrate(self, content_id: str, from_revision: str, save_data: dict) -> dict:
        """执行迁移链：从 from_revision 逐步迁移到最新版本。

        Args:
            content_id: 内容定义 ID
            from_revision: 存档中的版本号
            save_data: 存档数据

        Returns:
            迁移后的存档数据
        """
        current_rev = from_revision
        max_iterations = 20  # 防止循环
        for _ in range(max_iterations):
            plan = self.get_plan(content_id, current_rev)
            if plan is None:
                break
            save_data = plan.execute(save_data)
            current_rev = plan.to_revision
        return save_data

    def needs_migration(self, content_id: str, save_revision: str,
                        current_revision: str) -> bool:
        """判断是否需要迁移。"""
        return save_revision != current_revision
