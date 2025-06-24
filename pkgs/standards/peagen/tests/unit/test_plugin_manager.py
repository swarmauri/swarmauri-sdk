import sys
from importlib import reload

import pytest

import peagen.plugins as plugins
from peagen.plugins import PluginManager
from peagen.errors import InvalidPluginSpecError
from peagen.plugin_manager import resolve_plugin_spec

from .dummy_plugins import DummyQueue, DummyBackend


@pytest.mark.unit
def test_plugin_manager_instantiates_defaults(tmp_path):
    module_path = "tests.unit.dummy_plugins"
    sys.modules[module_path] = sys.modules[
        __name__.rsplit(".", 1)[0] + ".dummy_plugins"
    ]

    cfg = {
        "queues": {"default_queue": f"{module_path}:DummyQueue"},
        "result_backends": {
            "default_backend": f"{module_path}:DummyBackend",
            "adapters": {},
        },
    }

    pm = PluginManager(cfg)
    queue = pm.get("queues")
    backend = pm.get("result_backends")
    assert isinstance(queue, DummyQueue)
    assert isinstance(backend, DummyBackend)


@pytest.mark.unit
def test_plugin_manager_allows_null_default():
    cfg = {"queues": {"default_queue": None}}
    pm = PluginManager(cfg)
    assert pm.get("queues") is None


@pytest.mark.unit
def test_plugin_manager_allows_null_result_backend():
    cfg = {"result_backends": {"default_backend": None}}
    pm = PluginManager(cfg)
    assert pm.get("result_backends") is None


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

        class EP:
            name = "dummy"
            module = "peagen.dummy"

            def load(self):
                class Dummy:
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
        else:
            assert ep_group.startswith("peagen.plugins."), ep_group


@pytest.mark.unit
def test_resolve_plugin_spec_invalid():
    with pytest.raises(InvalidPluginSpecError):
        resolve_plugin_spec("evaluators", "invalid")
