# autoapi/v3/engine/engine_spec.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Mapping, Union, Any, Tuple

from ._engine import Engine, Provider, SessionFactory
from .builders import (
    async_postgres_engine,
    async_sqlite_engine,
    blocking_postgres_engine,
    blocking_sqlite_engine,
)

# The value stored by @engine_ctx on App/API/Table/Op.
# Accept either a DSN string, structured mapping, or pre-built objects.
EngineCtx = Union[str, Mapping[str, object], "EngineSpec", Provider, Engine]


@dataclass
class EngineSpec:
    """
    Canonical, normalized engine spec → Provider factory.

    Input comes from @engine_ctx attached to an App/API/Table/Op:
      • DSN string:
          "sqlite://:memory:" ,
          "sqlite:///./file.db" ,
          "sqlite+aiosqlite:///./file.db" ,
          "postgresql://user:pwd@host:5432/db" ,
          "postgresql+asyncpg://user:pwd@host:5432/db"
      • Mapping (recommended for clarity/portability):
          {
            "kind": "sqlite" | "postgres",
            "async": bool,                 # default False
            # sqlite:
            "path": "./file.db",           # file-backed
            "mode": "memory" | None,       # memory uses StaticPool
            # postgres:
            "user": "app", "pwd": "secret",
            "host": "localhost", "port": 5432, "db": "app_db",
            "pool_size": 10, "max": 20     # max_overflow (sync) or max_size (async)
          }

    This class *does not* open connections; call .to_provider() to obtain
    a lazy Provider that builds (engine, sessionmaker) on first use.
    """

    # normalized fields
    kind: Optional[str] = None  # "sqlite" | "postgres"
    async_: bool = False

    # sqlite
    path: Optional[str] = None  # file path (None when memory=True)
    memory: bool = False

    # postgres
    user: str = "app"
    pwd: str = "secret"
    host: str = "localhost"
    port: int = 5432
    name: str = "app_db"
    pool_size: int = 10
    max: int = 20  # max_overflow (sync) or max_size (async)

    # raw passthroughs (for diagnostics)
    dsn: Optional[str] = None
    mapping: Optional[Mapping[str, object]] = None

    # ---------- parsing / normalization ----------

    @staticmethod
    def from_any(x: EngineCtx | None) -> Optional["EngineSpec"]:
        """
        Parse a DSN or mapping (as attached by @engine_ctx) into an EngineSpec.
        """
        if x is None:
            return None

        if isinstance(x, EngineSpec):
            return x

        if isinstance(x, Provider):
            return x.spec

        if isinstance(x, Engine):
            return x.spec

        # String DSN
        if isinstance(x, str):
            s = x.strip()
            # sqlite memory
            if s == "sqlite://:memory:" or s.startswith("sqlite+memory://"):
                return EngineSpec(
                    kind="sqlite",
                    async_=s.startswith("sqlite+aiosqlite://"),
                    memory=True,
                    dsn=s,
                )
            # sqlite async file
            if s.startswith("sqlite+aiosqlite:///"):
                return EngineSpec(
                    kind="sqlite", async_=True, path=s.split(":///")[1], dsn=s
                )
            # sqlite sync file
            if s.startswith("sqlite:///"):
                return EngineSpec(
                    kind="sqlite", async_=False, path=s.split(":///")[1], dsn=s
                )
            # postgres async
            if s.startswith("postgresql+asyncpg://"):
                return EngineSpec(kind="postgres", async_=True, dsn=s)
            # postgres sync
            if s.startswith("postgresql://"):
                return EngineSpec(kind="postgres", async_=False, dsn=s)
            raise ValueError(f"Unsupported DSN: {s}")

        # Mapping
        m = x  # type: ignore[assignment]

        # allow a few common aliases for ergonomics
        def _get_bool(key: str, *aliases: str, default: bool = False) -> bool:
            for k in (key, *aliases):
                if k in m:
                    return bool(m[k])  # type: ignore[index]
            return default

        def _get_str(
            key: str, *aliases: str, default: Optional[str] = None
        ) -> Optional[str]:
            for k in (key, *aliases):
                if k in m and m[k] is not None:
                    return str(m[k])  # type: ignore[index]
            return default

        def _get_int(key: str, *aliases: str, default: int) -> int:
            for k in (key, *aliases):
                if k in m and m[k] is not None:
                    return int(m[k])  # type: ignore[index]
            return default

        k = str(m.get("kind", m.get("engine", ""))).lower()  # type: ignore[index]
        if k == "sqlite":
            async_ = _get_bool("async", "async_", default=False)
            path = _get_str("path")
            # support either {"mode": "memory"} or {"memory": True} or no path
            memory = (
                _get_bool("memory", default=False)
                or (str(m.get("mode", "")).lower() == "memory")
                or (path is None)
            )
            return EngineSpec(
                kind="sqlite",
                async_=async_,
                path=None if memory else path,
                memory=memory,
                mapping=m,
            )

        if k == "postgres":
            async_ = _get_bool("async", "async_", default=False)
            return EngineSpec(
                kind="postgres",
                async_=async_,
                user=_get_str("user", default="app") or "app",
                pwd=_get_str("pwd", "password", default="secret") or "secret",
                host=_get_str("host", default="localhost") or "localhost",
                port=_get_int("port", default=5432),
                name=_get_str("db", "name", default="app_db") or "app_db",
                pool_size=_get_int("pool_size", default=10),
                max=_get_int("max", "max_overflow", "max_size", default=20),
                mapping=m,
            )

        raise ValueError(f"Unsupported provider kind: {k!r}")

    # ---------- realization ----------

    def build(self) -> Tuple[Any, SessionFactory]:
        """Construct the engine and sessionmaker for this spec."""
        if self.kind == "sqlite":
            if self.memory:
                if self.async_:
                    return async_sqlite_engine(path=None)
                return blocking_sqlite_engine(path=None)
            if not self.path:
                raise ValueError("sqlite file requires 'path'")
            if self.async_:
                return async_sqlite_engine(path=self.path)
            return blocking_sqlite_engine(path=self.path)

        if self.kind == "postgres":
            if self.async_:
                return async_postgres_engine(
                    user=self.user,
                    pwd=self.pwd,
                    host=self.host,
                    port=self.port,
                    db=self.name,
                    pool_size=self.pool_size,
                    max_size=self.max,
                )
            return blocking_postgres_engine(
                user=self.user,
                pwd=self.pwd,
                host=self.host,
                port=self.port,
                db=self.name,
                pool_size=self.pool_size,
                max_overflow=self.max,
            )

        raise ValueError("EngineSpec has no kind")

    def to_provider(self) -> Provider:
        """Materialize a lazy :class:`Provider` for this spec."""
        return Provider(self)
