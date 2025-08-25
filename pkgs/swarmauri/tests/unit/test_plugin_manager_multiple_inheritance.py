from types import SimpleNamespace
from copy import deepcopy

from pydantic import BaseModel

from swarmauri_base import register_model
from swarmauri_base.DynamicBase import DynamicBase
from swarmauri.plugin_manager import _process_class_plugin
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry
from swarmauri.interface_registry import InterfaceRegistry


# Backup registries
_original_interface_registry = deepcopy(InterfaceRegistry.INTERFACE_REGISTRY)
_original_import_paths = deepcopy(InterfaceRegistry.INTERFACE_IMPORT_PATHS)
_original_first = deepcopy(PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY)
_original_second = deepcopy(PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY)
_original_third = deepcopy(PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY)
_original_known = PluginCitizenshipRegistry._KNOWN_GROUPS_CACHE
_original_dynamic = deepcopy(DynamicBase._registry)


@register_model()
class BaseX(DynamicBase):
    pass


@register_model()
class BaseY(DynamicBase):
    pass


@register_model(mixin=True)
class MixinX(BaseModel):
    pass


class Plugin(BaseX, BaseY, MixinX):
    pass


def test_registers_only_base_interfaces():
    InterfaceRegistry.register_interface("swarmauri.test_x", BaseX)
    InterfaceRegistry.register_interface("swarmauri.test_y", BaseY)
    InterfaceRegistry.register_interface("swarmauri.test_m", MixinX)

    ep = SimpleNamespace(name="Plugin", group="swarmauri.test_x", value="pkg:Plugin")
    assert _process_class_plugin(ep, "swarmauri.test_x.Plugin", Plugin, None)

    assert "swarmauri.test_x.Plugin" in PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert "swarmauri.test_y.Plugin" in PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert (
        "swarmauri.test_m.Plugin" not in PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    )

    InterfaceRegistry.unregister_interface("swarmauri.test_x")
    InterfaceRegistry.unregister_interface("swarmauri.test_y")
    InterfaceRegistry.unregister_interface("swarmauri.test_m")


def teardown_module():
    InterfaceRegistry.INTERFACE_REGISTRY = deepcopy(_original_interface_registry)
    InterfaceRegistry.INTERFACE_IMPORT_PATHS = deepcopy(_original_import_paths)
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = deepcopy(_original_first)
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY = deepcopy(_original_second)
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY = deepcopy(_original_third)
    PluginCitizenshipRegistry._KNOWN_GROUPS_CACHE = _original_known
    DynamicBase._registry = deepcopy(_original_dynamic)
