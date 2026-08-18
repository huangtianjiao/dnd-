"""规则一致性矩阵 — RuleConformanceMatrix（改造方案 §13.2）。

每条规则定义拥有唯一 rule_id 与来源元数据，按
DECLARED → STRUCTURED → IMPLEMENTED → WIRED → PERSISTED → E2E_VERIFIED
逐级提升；matrix 输出作为 CI 门禁的最小报告，证明"规则从定义到
玩家最终存档状态"的接线程度，而不是只证明"某模块被测试过"。

规则依据: DND5e2024_AIDM_完整改造实施方案 v1.0 §13.1-§13.3
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum


class RawStatus(StrEnum):
    """规则一致性等级（方案 §13.3）。

    - DECLARED: 规则在 ruleset/manifest 中有唯一 ID 与来源
    - STRUCTURED: 有可验证结构数据
    - IMPLEMENTED: 有 deterministic 实现
    - WIRED: 生产入口确实调用实现
    - PERSISTED: 结果进入 canonical state
    - E2E_VERIFIED: API/AI 场景 save→reload 后最终状态正确
    """

    DECLARED = "DECLARED"
    STRUCTURED = "STRUCTURED"
    IMPLEMENTED = "IMPLEMENTED"
    WIRED = "WIRED"
    PERSISTED = "PERSISTED"
    E2E_VERIFIED = "E2E_VERIFIED"


@dataclass
class RuleRecord:
    """单条规则的一致性记录。"""

    rule_id: str                          # 唯一规则 ID（如 "R-DRV-001"）
    edition: str = "2024"
    source_id: str = ""                   # content pack / 源标识（如 srd_5.2.1_core）
    source_anchor: str = ""               # 官方源锚点（如 PHB2024 页/节）
    domain: str = ""                      # character / class / spell / combat / rest ...
    # 接线状态位（all False 即 DECLARED）
    structured: bool = False
    implemented: bool = False
    wired: bool = False
    persisted: bool = False
    api_verified: bool = False
    ai_verified: bool = False
    e2e_verified: bool = False
    raw_status: str = RawStatus.DECLARED.value
    house_rule_override: str | None = None
    tests: list[str] = field(default_factory=list)
    last_verified: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> RuleRecord:
        valid = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in valid})

    def status(self) -> RawStatus:
        """按位推得当前等级（与 raw_status 字段互相校验）。"""
        if self.e2e_verified:
            return RawStatus.E2E_VERIFIED
        if self.persisted:
            return RawStatus.PERSISTED
        if self.wired:
            return RawStatus.WIRED
        if self.implemented:
            return RawStatus.IMPLEMENTED
        if self.structured:
            return RawStatus.STRUCTURED
        return RawStatus.DECLARED


class RuleConformanceMatrix:
    """规则一致性矩阵注册表 — 有序保存规则记录。"""

    def __init__(self) -> None:
        self._records: dict[str, RuleRecord] = {}

    def register(self, record: RuleRecord) -> RuleConformanceMatrix:
        if record.rule_id in self._records:
            raise ValueError(f"rule_id 重复注册: {record.rule_id}")
        self._records[record.rule_id] = record
        return self

    def get(self, rule_id: str) -> RuleRecord | None:
        return self._records.get(rule_id)

    def __iter__(self):
        return iter(self._records.values())

    def __len__(self) -> int:
        return len(self._records)

    def to_dict(self) -> dict:
        return {
            "rules": [r.to_dict() for r in self._records.values()],
            "count": len(self._records),
            "summary": self.summary(),
        }

    def summary(self) -> dict:
        """按等级统计（CI 最小输出）。"""
        counts: dict[str, int] = {}
        for r in self._records.values():
            counts[r.raw_status] = counts.get(r.raw_status, 0) + 1
        return {
            "by_status": dict(sorted(counts.items())),
            "total": len(self._records),
        }

    def json_report(self, indent: int = 2) -> str:
        """JSON 报告（写文件 / CI 输出用）。"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ──────────────────────────────────────────────────────────────────────────
# 默认矩阵：第一批规则（方案第 21 节第一轮任务 2-8 的落地规则）
# ──────────────────────────────────────────────────────────────────────────

def load_default_matrix() -> RuleConformanceMatrix:
    """加载项目内置规则一致性矩阵（第一批注册规则）。

    后续每个改造阶段在此追加规则（或迁移为从 ruleset/*/manifest 自动展开），
    禁止通过散落 if/else 形成隐式规则。
    """
    m = RuleConformanceMatrix()
    m.register(RuleRecord(
        rule_id="R-DRV-001",
        source_id="srd_5.2.1_core",
        source_anchor="PHB2024 角色创建：能力值",
        domain="character",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_state_authority.py::TestServerAuthoritativeStats",
               "tests/test_baseline_v1.py::TestDeriveStatsAuthority"],
        last_verified="2026-08-14",
    ))

    m.register(RuleRecord(
        rule_id="R-RSM-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §2.2 机械基线 / §2.1 规则模式",
        domain="campaign",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_baseline_v1.py::TestRulesetManifestV2",
               "tests/test_baseline_v1.py::TestCampaignRulesMode"],
        last_verified="2026-08-14",
    ))

    m.register(RuleRecord(
        rule_id="R-GRC-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §5.3 Grant/Choice provenance",
        domain="character",
        structured=True, implemented=True, wired=False, persisted=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_baseline_v1.py::TestCharacterGrantsPersistent"],
        last_verified="2026-08-14",
    ))

    m.register(RuleRecord(
        rule_id="R-CON-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §13.2 RuleConformanceMatrix",
        domain="governance",
        structured=True, implemented=True, wired=True, persisted=False,
        raw_status=RawStatus.IMPLEMENTED.value,
        tests=["tests/test_baseline_v1.py::TestConformanceMatrix"],
        last_verified="2026-08-14",
    ))

    m.register(RuleRecord(
        rule_id="R-FGT-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §7.1 Fighter 1-20 progression 覆盖",
        domain="class",
        structured=True, implemented=True, wired=False, persisted=False,
        raw_status=RawStatus.IMPLEMENTED.value,
        tests=["tests/test_baseline_v1.py::TestFighterGoldenSnapshots",
               "tests/test_edition_regression_2024.py::TestFighterIndomitableProgression"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-BLD-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §6.1 唯一构建服务 / §5.3 provenance",
        domain="character",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p3_character_builder.py"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-CHC-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §6.3/§8.3 pending choices API",
        domain="character",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p3_character_builder.py::TestPendingChoicesApi"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-EDT-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §13.4 2014 污染回归套件",
        domain="governance",
        structured=False, implemented=False, wired=False, persisted=False,
        raw_status=RawStatus.DECLARED.value,
        tests=["tests/test_edition_regression_2024.py"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-FTR-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §8.2 FeatEntitlementService",
        domain="character",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p5_entitlement_levelup.py::TestFeatEntitlement",
               "tests/test_edition_regression_2024.py::TestFeatASIDrivenByClassProgression"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-PRE-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §4.4 PrerequisiteEvaluator",
        domain="character",
        structured=True, implemented=True, wired=False, persisted=False,
        raw_status=RawStatus.IMPLEMENTED.value,
        tests=["tests/test_p5_entitlement_levelup.py::TestPrerequisiteEvaluator"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-LVL-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §8.1 LevelUpPlan / §8.3 Choice API",
        domain="character",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p5_entitlement_levelup.py::TestLevelUpPipeline"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-MC-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §8.4 MulticlassService 收敛（brain 委托 engine）",
        domain="character",
        structured=True, implemented=True, wired=True, persisted=False,
        api_verified=True,
        raw_status=RawStatus.IMPLEMENTED.value,
        tests=["tests/test_p5_entitlement_levelup.py::TestMulticlassConvergence"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-SPL-101",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §10.2/§10.3 来源分离与 prepare 唯一路径",
        domain="spellcasting",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p7_spellcasting.py"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-RST-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §9.2 RestService 事务",
        domain="rest",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p6_rest_health.py::TestRestTransaction"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-HLT-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §9.4 HealthService 状态机",
        domain="combat",
        structured=True, implemented=True, wired=False, persisted=False,
        raw_status=RawStatus.IMPLEMENTED.value,
        tests=["tests/test_p6_rest_health.py::TestHealthService"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-RES-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §9.1/§5.4 资源池持久化",
        domain="character",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p6_rest_health.py::TestResourcePoolPersistence"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-MAS-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §11.2 MasteryGrant",
        domain="combat",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p8_mastery_trace.py::TestMasteryGrantPersistence",
               "tests/test_p8_mastery_trace.py::TestMasteryAuthorizationGate"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-TRC-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §11.4 ResolutionTrace",
        domain="combat",
        structured=True, implemented=True, wired=True, persisted=False,
        raw_status=RawStatus.IMPLEMENTED.value,
        tests=["tests/test_p8_mastery_trace.py::TestResolutionTrace"],
        last_verified="2026-08-14",
    ))
    m.register(RuleRecord(
        rule_id="R-LGC-001",
        source_id="srd_5.2.1_core",
        source_anchor="改造方案 §14.4 Legacy 删除清单",
        domain="governance",
        structured=True, implemented=True, wired=True, persisted=True,
        api_verified=True,
        raw_status=RawStatus.PERSISTED.value,
        tests=["tests/test_p10_legacy_removal.py"],
        last_verified="2026-08-14",
    ))
    return m
