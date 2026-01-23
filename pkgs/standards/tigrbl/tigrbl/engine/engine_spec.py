# tigrbl/v3/engine/engine_spec.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Mapping, Union, Any, Tuple
from urllib.parse import urlsplit, urlunsplit

from ._engine import Engine, Provider, SessionFactory
from .builders import (
    async_postgres_engine,
    async_sqlite_engine,
    blocking_postgres_engine,
    blocking_sqlite_engine,
)

# The value stored by @engine_ctx on App/API/Table/Op.
EngineCfg = Union[str, Mapping[str, object], "EngineSpec", Provider, Engine]


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
          {"kind":"sqlite","async":True,"path":"./file.db"}
          {"kind":"postgres","async":True,"host":"db","db":"app_db",...}
          {<external kind> ...}  # for plugin engines
    """

    # normalized
    kind: Optional[str] = None  # "sqlite" | "postgres" | <external>
    async_: bool = False

    # canonical DSN (optional) and raw mapping (for external engines)
    dsn: Optional[str] = None
    mapping: Optional[Mapping[str, object]] = None

    # sqlite
    path: Optional[str] = None  # file path (None → memory)
    memory: bool = False

    # postgres
    user: Optional[str] = None
    pwd: Optional[str] = field(default=None, repr=False)
    host: Optional[str] = None
    port: Optional[int] = None
    name: Optional[str] = None
    pool_size: int = 10
    max: int = 20  # max_overflow (sync) or max_size (async)

    # ---------- parsing ----------

    @staticmethod
    def from_any(x: EngineCfg | None) -> Optional["EngineSpec"]:
        """Parse DSN/Mapping/Provider/Engine into an :class:`EngineSpec`."""
        if x is None:
            return None

        if isinstance(x, EngineSpec):
            return x

        if isinstance(x, Provider):
            return x.spec

        if isinstance(x, Engine):
            return x.spec

        # DSN string
        if isinstance(x, str):
            s = x.strip()
            # sqlite async
            if s.startswith("sqlite+aiosqlite://") or s.startswith("sqlite+aiosqlite:"):
                path = urlsplit(s).path or ""
                if s.startswith("sqlite+aiosqlite:////"):
                    if path.startswith("//"):
                        path = path[1:]
                    path = path or None
                else:
                    path = path.lstrip("/") or None
                mem = path in {None, ":memory:", "/:memory:"} or s.endswith(":memory:")
                return EngineSpec(
                    kind="sqlite", async_=True, path=path, memory=mem, dsn=s
                )
            # sqlite sync
            if s.startswith("sqlite://") or s.startswith("sqlite:"):
                # handle sqlite://:memory: and sqlite:///file.db
                if s.startswith("sqlite://:memory:") or s.endswith(":memory:"):
                    return EngineSpec(
                        kind="sqlite", async_=False, path=None, memory=True, dsn=s
                    )
                # Take the path part after scheme; urlsplit handles both sqlite:// and sqlite:/// forms
                p = urlsplit(s).path or ""
                if s.startswith("sqlite:////"):
                    if p.startswith("//"):
                        p = p[1:]
                    p = p or None
                else:
                    p = p.lstrip("/") or None
                mem = p is None
                return EngineSpec(
                    kind="sqlite", async_=False, path=p, memory=mem, dsn=s
                )

            # postgres async
            if s.startswith("postgresql+asyncpg://") or s.startswith(
                "postgres+asyncpg://"
            ):
                return EngineSpec(kind="postgres", async_=True, dsn=s)
            # postgres sync
            if s.startswith("postgresql://") or s.startswith("postgres://"):
                return EngineSpec(kind="postgres", async_=False, dsn=s)

            raise ValueError(f"Unsupported DSN: {s}")

        # Mapping
        m = x  # type: ignore[assignment]

        # Helpers
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

        def _get_int(
            key: str, *aliases: str, default: Optional[int] = None
        ) -> Optional[int]:
            for k in (key, *aliases):
                if k in m and m[k] is not None:
                    try:
                        return int(m[k])  # type: ignore[index]
                    except Exception:
                        return default
            return default

        k = str(m.get("kind", m.get("engine", ""))).lower()  # type: ignore[index]
        if k == "sqlite":
            async_ = _get_bool("async", "async_", default=False)
            path = _get_str("path")
            memory = (
                _get_bool("memory", default=False)
                or (str(m.get("mode", "")).lower() == "memory")
                or (path is None)
            )
            return EngineSpec(
                kind="sqlite",
                async_=async_,
                path=path,
                memory=memory,
                dsn=_get_str("dsn", "url"),
                mapping=m,
            )

        if k == "postgres":
            async_ = _get_bool("async", "async_", default=False)
            return EngineSpec(
                kind="postgres",
                async_=async_,
                user=_get_str("user"),
                pwd=_get_str("pwd", "password"),
                host=_get_str("host"),
                port=_get_int("port"),
                name=_get_str("db", "name"),
                pool_size=_get_int("pool_size", default=10) or 10,
                max=_get_int("max", "max_overflow", "max_size", default=20) or 20,
                dsn=_get_str("dsn", "url"),
                mapping=m,
            )

        # External / unknown kinds – keep mapping and defer to registry at build()
        return EngineSpec(
            kind=k or None,
            async_=_get_bool("async", "async_", default=False),
            dsn=_get_str("dsn", "url"),
            mapping=m,
        )

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
            if self.dsn:
                if self.async_:
                    return async_postgres_engine(dsn=self.dsn)
                return blocking_postgres_engine(dsn=self.dsn)
            # keyword build
            kwargs: dict[str, Any] = {
                "user": self.user or "app",
                "host": self.host or "localhost",
                "port": self.port or 5432,
                "db": self.name or "app_db",
                "pool_size": int(self.pool_size or 10),
            }
            if self.pwd is not None:
                kwargs["pwd"] = self.pwd
            if self.async_:
                kwargs["max_size"] = int(self.max or 20)
                return async_postgres_engine(**kwargs)
            else:
                kwargs["max_overflow"] = int(self.max or 20)
                return blocking_postgres_engine(**kwargs)

        # External/registered engines
        try:
            from .plugins import load_engine_plugins
            from .registry import get_engine_registration, known_engine_kinds

            load_engine_plugins()
            reg = get_engine_registration(self.kind or "")
        except Exception:
            reg = None
        if reg:
            mapping = self.mapping or {}
            return reg.build(mapping=mapping, spec=self, dsn=self.dsn)

        # No registration found: helpful error
        try:
            from .registry import known_engine_kinds  # re-import defensive

            kinds = ", ".join(known_engine_kinds()) or "(none)"
        except Exception:
            kinds = "(unknown)"
        raise RuntimeError(
            f"Unknown or unavailable engine kind '{self.kind}'. Installed engine kinds: {kinds}. "
            f"If this is an optional extension, install its package (e.g., 'pip install tigrbl_engine_{self.kind}')."
        )

    def supports(self) -> dict[str, Any]:
        """Return capability dictionary for this engine spec.
        For external kinds, consult the plugin registry if available.
        """
        # Built-ins
        if self.kind == "sqlite":
            try:
                from .capabilities import sqlite_capabilities

                return sqlite_capabilities(async_=self.async_, memory=self.memory)
            except Exception:
                pass
        if self.kind == "postgres":
            try:
                from .capabilities import postgres_capabilities

                return postgres_capabilities(async_=self.async_)
            except Exception:
                pass
        # External/registered engines
        try:
            from .plugins import load_engine_plugins
            from .registry import get_engine_registration

            load_engine_plugins()
            reg = get_engine_registration(self.kind or "")
        except Exception:
            reg = None
        if reg and getattr(reg, "capabilities", None):
            try:
                # Try flexible signature: capabilities(spec=..., mapping=...)
                return reg.capabilities(spec=self, mapping=self.mapping)
            except TypeError:
                try:
                    return reg.capabilities()
                except Exception:
                    pass
            except Exception:
                pass
        # Fallback minimal shape
        return {
            "transactional": False,
            "async_native": bool(self.async_),
            "isolation_levels": set(),
            "read_only_enforced": False,
            "engine": self.kind or "unknown",
        }

    def to_provider(self) -> Provider:
        """Materialize a lazy :class:`Provider` for this spec."""
        return Provider(self)

    def __repr__(self) -> str:  # pragma: no cover - deterministic output
        def _redact_dsn(dsn: Optional[str]) -> Optional[str]:
            if not dsn:
                return dsn
            try:
                parts = urlsplit(dsn)
            except Exception:
                return dsn
            if not parts.scheme or parts.password is None:
                return dsn
            user = parts.username or ""
            userinfo = f"{user}:***" if user else "***"
            host = parts.hostname or ""
            netloc = f"{userinfo}@{host}" if host else userinfo
            if parts.port is not None:
                netloc = f"{netloc}:{parts.port}"
            return urlunsplit(
                (parts.scheme, netloc, parts.path, parts.query, parts.fragment)
            )

        def _redact_mapping(
            mapping: Optional[Mapping[str, object]],
        ) -> Optional[dict[str, object]]:
            if mapping is None:
                return None
            redacted: dict[str, object] = {}
            for key, value in mapping.items():
                if str(key).lower() in {"pwd", "password", "pass", "secret"}:
                    redacted[key] = "***"
                else:
                    redacted[key] = value
            return redacted

        fields = [
            ("kind", self.kind),
            ("async_", self.async_),
            ("dsn", _redact_dsn(self.dsn)),
            ("mapping", _redact_mapping(self.mapping)),
            ("path", self.path),
            ("memory", self.memory),
            ("user", self.user),
            ("host", self.host),
            ("port", self.port),
            ("name", self.name),
            ("pool_size", self.pool_size),
            ("max", self.max),
        ]
        return "EngineSpec(" + ", ".join(f"{k}={v!r}" for k, v in fields) + ")"
