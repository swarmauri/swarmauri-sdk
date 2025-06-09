import sys
import pytest

from peagen.plugins import PluginManager

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
