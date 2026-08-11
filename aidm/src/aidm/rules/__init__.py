"""rules 包 — Feature DSL / Grant / Choice / ResourcePool 基础框架"""

from aidm.rules.feature_dsl import FeatureDefinition, FeatureType
from aidm.rules.grant import Grant, GrantManager
from aidm.rules.choice import ChoiceManager, ChoiceRecord, ChoiceRequest
from aidm.rules.resource import ResourceManager, ResourcePool

__all__ = [
    "FeatureDefinition",
    "FeatureType",
    "Grant",
    "GrantManager",
    "ChoiceManager",
    "ChoiceRecord",
    "ChoiceRequest",
    "ResourceManager",
    "ResourcePool",
]
