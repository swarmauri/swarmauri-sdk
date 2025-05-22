import sys
import types
import importlib.metadata as im

import pytest

from peagen import plugin_registry


@pytest.fixture(autouse=True)
def clear_registry():
    plugin_registry.registry.clear()
    yield
    plugin_registry.registry.clear()


def _make_ep(name: str, module_name: str, obj_name: str, group: str):
    mod = types.ModuleType(module_name)
    cls = type(obj_name, (), {})
    setattr(mod, obj_name, cls)
    sys.modules[module_name] = mod
    return im.EntryPoint(name, f"{module_name}:{obj_name}", group), cls


@pytest.mark.unit
def test_discover_and_register_plugins(monkeypatch):
    ep1, cls1 = _make_ep("builtin", "peagen.builtin_mod", "Builtin", "peagen.storage_adapters")
    ep2, cls2 = _make_ep("external", "ext.mod", "External", "peagen.storage_adapters")

    def fake_entry_points(group: str):
        if group == "peagen.storage_adapters":
            return [ep1, ep2]
        return []

    monkeypatch.setattr(plugin_registry, "entry_points", fake_entry_points)

    plugin_registry.discover_and_register_plugins()

    assert plugin_registry.registry["storage_adapters"]["builtin"] is cls1
    assert plugin_registry.registry["storage_adapters"]["external"] is cls2


@pytest.mark.unit
def test_duplicate_plugin_raises(monkeypatch):
    ep1, _ = _make_ep("name", "peagen.mod1", "A", "peagen.storage_adapters")
    ep2, _ = _make_ep("name", "ext.mod1", "B", "peagen.storage_adapters")

    def fake_entry_points(group: str):
        if group == "peagen.storage_adapters":
            return [ep1, ep2]
        return []

    monkeypatch.setattr(plugin_registry, "entry_points", fake_entry_points)

    with pytest.raises(RuntimeError):
        plugin_registry.discover_and_register_plugins()


@pytest.mark.unit
def test_fallback_mode_skips_duplicate(monkeypatch):
    ep1, cls1 = _make_ep("name", "peagen.mod2", "A", "peagen.storage_adapters")
    ep2, _ = _make_ep("name", "ext.mod2", "B", "peagen.storage_adapters")

    def fake_entry_points(group: str):
        if group == "peagen.storage_adapters":
            return [ep1, ep2]
        return []

    monkeypatch.setattr(plugin_registry, "entry_points", fake_entry_points)

    plugin_registry.discover_and_register_plugins(mode="fallback")

    assert plugin_registry.registry["storage_adapters"]["name"] is cls1
