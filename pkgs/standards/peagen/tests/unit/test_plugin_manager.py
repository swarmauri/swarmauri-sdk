import types
from peagen.plugin_manager import resolve_plugin_spec
from peagen.plugins import registry

class DummyPool:
    pass


def test_resolve_plugin_spec_from_registry(monkeypatch):
    monkeypatch.setitem(registry.setdefault("evaluator_pools", {}), "dummy", DummyPool)
    assert resolve_plugin_spec("evaluator_pools", "dummy") is DummyPool


def test_resolve_plugin_spec_dotted_path():
    cls = resolve_plugin_spec(
        "evaluator_pools",
        "peagen.plugins.evaluator_pools.default:DefaultEvaluatorPool",
    )
    assert cls.__name__.endswith("EvaluatorPool")

