from __future__ import annotations

from dataclasses import dataclass

from tigrbl_concrete._concrete._engine import EngineProvider


@dataclass
class _FakeSpec:
    kind: str = "sqlite"
    async_: bool = False
    path: str | None = "db.sqlite"
    pool: str | None = None
    user: str | None = None
    pwd: str | None = None
    host: str | None = None
    port: int | None = None
    name: str | None = None
    pool_size: int = 10
    max: int = 20

    def build(self):
        raise RuntimeError(
            "Unknown or unavailable engine kind 'sqlite'. Installed engine kinds: (none)."
        )


def test_engine_provider_uses_concrete_builder_fallback(monkeypatch):
    from tigrbl_concrete.engine import builders

    monkeypatch.setattr(
        builders,
        "blocking_sqlite_engine",
        lambda **kw: ("sync_sqlite", lambda: kw),
    )

    provider = EngineProvider(_FakeSpec())
    engine, maker = provider.ensure()

    assert engine == "sync_sqlite"
    assert maker() == {"path": "db.sqlite", "pool": None}
