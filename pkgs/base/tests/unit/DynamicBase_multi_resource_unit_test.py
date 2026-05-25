"""Unit tests for registering to multiple resource types."""

import pytest

from swarmauri_base.DynamicBase import DynamicBase


@DynamicBase.register_model()
class ResourceTypeA(DynamicBase):
    """Dummy base model A."""


@DynamicBase.register_model()
class ResourceTypeB(DynamicBase):
    """Dummy base model B."""


@DynamicBase.register_type(resource_type=(ResourceTypeA, ResourceTypeB))
class MultiResource(ResourceTypeA, ResourceTypeB):
    """Model registered to two resource types."""


@pytest.mark.unit
def test_register_multiple_resource_types():
    """Ensure a model registers under each specified resource type."""
    reg_a = DynamicBase._registry["ResourceTypeA"]["subtypes"]
    reg_b = DynamicBase._registry["ResourceTypeB"]["subtypes"]
    assert reg_a["MultiResource"] is MultiResource
    assert reg_b["MultiResource"] is MultiResource
