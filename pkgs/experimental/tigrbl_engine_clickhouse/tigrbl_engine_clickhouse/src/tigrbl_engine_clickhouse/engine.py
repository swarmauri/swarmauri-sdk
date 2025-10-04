from __future__ import annotations
from typing import Any, Callable, Tuple, Mapping, Optional

from tigrbl.engine._engine import Engine  # first-class engine façade
from .session import ClickHouseSession

class ClickHouseEngine(Engine):
    """Thin handle for ClickHouse connectivity parameters.

    Subclasses tigrbl's first-class :class:`Engine` for parity with built-ins.
    The session owns the actual driver client.
    """
    def __init__(
        self,
        *,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        secure: Optional[bool] = None,
        verify: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        self.url = url
        self.host = host or "localhost"
        self.port = int(port or 8123)
        self.username = username or "default"
        self.password = password or ""
        self.database = database or "default"
        self.secure = bool(secure) if secure is not None else False
        self.verify = bool(verify) if verify is not None else True
        self.kwargs = dict(kwargs)

def clickhouse_engine(
    *,
    mapping: Optional[Mapping[str, object]] = None,
    spec: Any = None,
    dsn: Optional[str] = None,
    **kwargs: Any
) -> Tuple[ClickHouseEngine, Callable[[], Any]]:
    """Builder used by tigrbl to construct (engine, session_factory)."""
    m = dict(mapping or {})
    engine = ClickHouseEngine(
        url = dsn or m.get("url") or kwargs.get("url"),
        host = m.get("host") or kwargs.get("host"),
        port = m.get("port") or kwargs.get("port"),
        username = m.get("username") or kwargs.get("username"),
        password = m.get("password") or kwargs.get("password"),
        database = m.get("database") or kwargs.get("database"),
        secure = m.get("secure") or kwargs.get("secure"),
        verify = m.get("verify") or kwargs.get("verify"),
        **kwargs,
    )

    def session_factory() -> ClickHouseSession:
        return ClickHouseSession(engine)

    return engine, session_factory
