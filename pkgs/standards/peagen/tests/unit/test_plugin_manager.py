from importlib import reload

import pytest

import peagen.plugins as plugins
from peagen.plugins import PluginManager
from peagen.errors import InvalidPluginSpecError
from peagen.plugin_manager import resolve_plugin_spec

from .dummy_plugins import DummyQueue


@pytest.mark.unit
def test_plugin_manager_instantiates_defaults(tmp_path, monkeypatch):
    cfg = {
        "queues": {"default_queue": "dummy_queue"},
    }

    _reset_plugins(monkeypatch)
    monkeypatch.setattr(plugins, "entry_points", lambda group: [])

    pm = PluginManager(cfg)
    plugins.registry["queues"]["dummy_queue"] = DummyQueue

    queue = pm.get("queues")
    assert isinstance(queue, DummyQueue)


@pytest.mark.unit
def test_plugin_manager_allows_null_default():
    cfg = {"queues": {"default_queue": None}}
    pm = PluginManager(cfg)
    assert pm.get("queues") is None


def _reset_plugins(monkeypatch):
    reload(plugins)
    monkeypatch.setattr(plugins, "_DISCOVERED", False, raising=False)
    for group in plugins.registry:
        plugins.registry[group].clear()


@pytest.mark.unit
def test_plugin_discovery_runs_once(monkeypatch):
    _reset_plugins(monkeypatch)

    calls: list[str] = []

    def fake_entry_points(group: str):
        calls.append(group)

        # determine expected base class for this entry point group
        base_cls = object
        for _group, (ep_group, expected) in plugins.GROUPS.items():
            if ep_group == group:
                base_cls = expected or object
                break

        class EP:
            name = "dummy"
            module = "peagen.dummy"

            def load(self):
                class Dummy(base_cls):
                    pass

                return Dummy

        return [EP()]

    monkeypatch.setattr(plugins, "entry_points", fake_entry_points)

    PluginManager({})
    PluginManager({})

    assert len(calls) == len(plugins.GROUPS)


@pytest.mark.unit
def test_ep_paths_use_plugins_namespace():
    for group, (ep_group, _base) in plugins.GROUPS.items():
        if group == "template_sets":
            assert ep_group == "peagen.template_sets"
        elif group == "key_providers":
            assert ep_group == "swarmauri.key_providers"
        else:
            assert ep_group.startswith("peagen.plugins."), ep_group


@pytest.mark.unit
def test_resolve_plugin_spec_invalid():
    with pytest.raises(InvalidPluginSpecError):
        resolve_plugin_spec("evaluators", "invalid")
