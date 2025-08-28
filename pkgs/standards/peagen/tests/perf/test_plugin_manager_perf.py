import time
from importlib import reload

import pytest

import peagen.plugins as plugins
from peagen.plugins import PluginManager
from swarmauri_base.git_filters import GitFilterBase
from swarmauri_base.keys import KeyProviderBase


def _reset_plugins(monkeypatch):
    reload(plugins)
    monkeypatch.setattr(plugins, "_DISCOVERED", False, raising=False)
    for group in plugins.registry:
        plugins.registry[group].clear()


@pytest.mark.perf
def test_plugin_discovery_cached(monkeypatch):
    _reset_plugins(monkeypatch)

    def fake_entry_points(group: str):
        time.sleep(0.01)

        class EP:
            name = "dummy"
            module = "peagen.dummy"

            def load(self):
                if group == "swarmauri.key_providers":

                    class Dummy(KeyProviderBase):
                        pass
                elif group == "peagen.plugins.git_filters":

                    class Dummy(GitFilterBase):
                        pass
                else:

                    class Dummy:
                        pass

                return Dummy

        return [EP()]

    monkeypatch.setattr(plugins, "entry_points", fake_entry_points)

    start = time.perf_counter()
    PluginManager({})
    first = time.perf_counter() - start

    start = time.perf_counter()
    PluginManager({})
    second = time.perf_counter() - start

    assert second < first * 0.1
