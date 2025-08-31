# tests/test_engine_spec_and_shortcuts.py
import pytest

from autoapi.v3.engines.shortcuts import engS, prov, engine, mem, sqlitef, pg, pga, pgs  # :contentReference[oaicite:2]{index=2}
from autoapi.v3.engines.engine_spec import EngineSpec  # :contentReference[oaicite:3]{index=3}

def test_engS_builds_from_kwargs_sqlite_memory_async():
    spec = engS(kind="sqlite", mode="memory", async_=True)  # collapsed ctx builder
    assert isinstance(spec, EngineSpec)  # normalized
    assert spec.kind == "sqlite" and spec.async_ is True and spec.memory is True  # :contentReference[oaicite:4]{index=4}

def test_engS_builds_from_mapping_postgres_sync():
    spec = engS({"kind": "postgres", "async": False, "host": "db", "db": "foo"})  # mapping path
    assert spec.kind == "postgres" and spec.async_ is False and spec.host == "db"  # :contentReference[oaicite:5]{index=5}

def test_prov_lazily_constructs_and_sessions_are_fresh_sync(tmp_path):
    p = prov(sqlitef(str(tmp_path / "x.sqlite")))  # mapping helper → Provider  :contentReference[oaicite:6]{index=6}
    assert p.kind == "sync"
    s1 = p.session()
    s2 = p.session()
    assert s1 is not s2  # fresh sessions per call
    for s in (s1, s2):
        close = getattr(s, "close", None)
        if callable(close):
            close()

@pytest.mark.asyncio
async def test_engine_async_context_manager_ok():
    e = engine(mem(async_=True))  # async sqlite in-memory  :contentReference[oaicite:7]{index=7}
    # Just enter/exit; if builders are wired, this should pass
    async with e.asession() as s:
        # smoke: check basic API surface
        close = getattr(s, "close", None)
        assert close is not None
