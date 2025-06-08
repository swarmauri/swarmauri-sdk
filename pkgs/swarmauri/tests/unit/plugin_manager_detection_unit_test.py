import pytest
from importlib.metadata import EntryPoint

from swarmauri.plugin_manager import (
    is_plugin_class,
    is_plugin_module,
    is_plugin_generic,
)


@pytest.mark.unit
def test_is_plugin_class_true_for_class_reference():
    ep = EntryPoint(name="Test", value="pkg.module:ClassName", group="swarmauri.agents")
    assert is_plugin_class(ep)


@pytest.mark.unit
def test_is_plugin_module_true_when_no_attribute():
    ep = EntryPoint(name="Test", value="pkg.module", group="swarmauri.agents")
    assert is_plugin_module(ep)


@pytest.mark.unit
def test_is_plugin_generic_true_for_non_identifier_attribute():
    ep = EntryPoint(name="Test", value="pkg.module:some.attr", group="swarmauri.plugins")
    assert is_plugin_generic(ep)
