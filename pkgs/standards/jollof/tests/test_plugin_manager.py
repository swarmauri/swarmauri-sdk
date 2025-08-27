import json
from importlib.metadata import EntryPoint

from jollof.plugin_manager import PluginManager
from jollof.registry import PluginDomainRegistry
from .dummy_plugins import ExamplePlugin


def _fake_entry_points(group):
    if group == "example.group":
        ep = EntryPoint(
            name="ExamplePlugin",
            value="tests.dummy_plugins:ExamplePlugin",
            group="example.group",
        )
        return [ep]
    return []


def test_discover_and_load(monkeypatch):
    monkeypatch.setattr(
        "jollof.plugin_manager.entry_points",
        lambda group: _fake_entry_points(group),
    )
    pm = PluginManager(groups={"examples": ("example.group", ExamplePlugin)})
    pm.discover()
    inst = pm.load(
        "examples", "ExamplePlugin", json.dumps({"name": "a", "value": 1}), "json"
    )
    assert inst.value == 1
    dumped = pm.dump(inst, "yaml")
    reloaded = pm.load("examples", "ExamplePlugin", dumped, "yaml")
    assert reloaded.name == "a"


def test_manual_registration():
    pm = PluginManager()
    pm.register("examples", "ExamplePlugin", ExamplePlugin)
    assert PluginDomainRegistry.get("default", "examples", "ExamplePlugin")
