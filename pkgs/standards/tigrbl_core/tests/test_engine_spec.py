from __future__ import annotations

import sys
import types

import pytest

from tigrbl_core._spec.engine_spec import EngineProviderSpec, EngineSpec


def test_from_any_parses_sqlite_and_postgres_dsn() -> None:
    sqlite = EngineSpec.from_any("sqlite://:memory:")
    pg = EngineSpec.from_any("postgresql://user:pwd@localhost:5432/db")

    assert sqlite is not None and sqlite.kind == "sqlite" and sqlite.memory is True
    assert pg is not None and pg.kind == "postgres" and pg.async_ is False


def test_from_any_parses_mapping_aliases() -> None:
    spec = EngineSpec.from_any(
        {
            "engine": "postgres",
            "async": True,
            "password": "pw",
            "db": "app",
            "max_size": "11",
        }
    )

    assert spec is not None
    assert spec.kind == "postgres"
    assert spec.async_ is True
    assert spec.pwd == "pw"
    assert spec.name == "app"
    assert spec.max == 11


def test_from_any_rejects_unknown_dsn() -> None:
    with pytest.raises(ValueError, match="Unsupported DSN"):
        EngineSpec.from_any("oracle://local")


def test_build_uses_builder_module_for_sqlite() -> None:
    module = types.ModuleType("tigrbl_concrete.engine.builders")
    module.async_sqlite_engine = lambda **kw: ("async_sqlite", kw)
    module.blocking_sqlite_engine = lambda **kw: ("sync_sqlite", kw)
    module.async_postgres_engine = lambda **kw: ("async_pg", kw)
    module.blocking_postgres_engine = lambda **kw: ("sync_pg", kw)
    sys.modules[module.__name__] = module

    result = EngineSpec(
        kind="sqlite", async_=False, memory=False, path="db.sqlite"
    ).build()

    assert result == ("sync_sqlite", {"path": "db.sqlite", "pool": None})


def test_provider_from_any_wraps_spec_property() -> None:
    inner = EngineSpec(kind="sqlite", memory=True)

    class Obj:
        spec = inner

    provider = EngineProviderSpec.from_any(Obj())

    assert provider is not None
    assert provider.spec is inner


def test_repr_redacts_passwords() -> None:
    spec = EngineSpec(
        kind="postgres",
        dsn="postgresql://alice:secret@localhost:5432/db",
        mapping={"password": "secret", "name": "db"},
    )

    rendered = repr(spec)

    assert "secret" not in rendered
    assert "***" in rendered
