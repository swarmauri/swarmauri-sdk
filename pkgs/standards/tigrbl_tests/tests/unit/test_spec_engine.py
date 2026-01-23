import inspect

from tigrbl.engine._engine import Engine, Provider
from tigrbl.engine.decorators import engine_ctx
from tigrbl.engine.engine_spec import EngineSpec
from tigrbl.engine.shortcuts import engine as build_engine
from tigrbl.engine.shortcuts import engine_spec, mem, prov


def test_engine_spec_parses_sqlite_dsn():
    spec = EngineSpec.from_any("sqlite+aiosqlite:///:memory:")
    assert spec is not None
    assert spec.kind == "sqlite"
    assert spec.async_ is True
    assert spec.memory is True
    assert spec.dsn == "sqlite+aiosqlite:///:memory:"


def test_engine_spec_parses_mapping_defaults():
    spec = EngineSpec.from_any({"kind": "sqlite", "mode": "memory"})
    assert spec is not None
    assert spec.kind == "sqlite"
    assert spec.memory is True
    assert spec.async_ is False


def test_engine_spec_to_provider_roundtrip():
    spec = EngineSpec.from_any("sqlite://:memory:")
    assert spec is not None
    provider = spec.to_provider()
    assert isinstance(provider, Provider)
    assert provider.spec is spec


def test_engine_ctx_binds_to_functions_and_models():
    @engine_ctx("sqlite://:memory:")
    def handler():
        return None

    assert getattr(handler, "__tigrbl_engine_ctx__") == "sqlite://:memory:"
    assert getattr(handler, "__tigrbl_db__") == "sqlite://:memory:"

    @engine_ctx("sqlite://:memory:")
    class Widget:
        __tablename__ = "widgets"

    table_cfg = getattr(Widget, "table_config")
    assert table_cfg["engine"] == "sqlite://:memory:"
    assert table_cfg["db"] == "sqlite://:memory:"


def test_engine_shortcuts_build_expected_types():
    spec = engine_spec(mem())
    provider = prov(spec)
    engine = build_engine(spec)
    assert isinstance(spec, EngineSpec)
    assert isinstance(provider, Provider)
    assert isinstance(engine, Engine)
    assert engine.spec == spec
    assert engine.is_async is True
    assert inspect.isfunction(provider.get_db)
