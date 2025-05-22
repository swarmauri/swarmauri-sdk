import pytest
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

class DummyComponent(ComponentBase):
    pass

@pytest.mark.unit
def test_component_base_defaults():
    comp = DummyComponent()
    assert comp.resource == "ComponentBase"
    assert comp.type == "DummyComponent"
    assert comp.version == "0.1.0"

@pytest.mark.unit
def test_resource_types_contains_tool():
    assert ResourceTypes.TOOL.value == "Tool"
