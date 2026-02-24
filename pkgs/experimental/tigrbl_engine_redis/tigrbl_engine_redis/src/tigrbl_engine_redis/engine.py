from __future__ import annotations
from typing import Any, Callable, Tuple, Mapping, Optional

from tigrbl.engine._engine import Engine  # first-class engine façade
from .session import RedisSession


class RedisEngine(Engine):
    """Thin, inspectable handle for Redis connectivity parameters.

    This class subclasses tigrbl's first-class :class:`Engine`. It is **not**
    responsible for connection pooling — the session constructs and owns the
    actual Redis client.
    """

    def __init__(
        self,
        *,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        # We intentionally do not call super().__init__ because the base Engine
        # is a dataclass façade around EngineSpec. For plugin handles we only
        # need a lightweight, inspectable object.
        self.url = url
        self.host = host or "localhost"
        self.port = int(port or 6379)
        self.db = int(db or 0)
        self.kwargs = dict(kwargs)


def redis_engine(
    *,
    mapping: Optional[Mapping[str, object]] = None,
    spec: Any = None,
    dsn: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[RedisEngine, Callable[[], Any]]:
    """Builder function used by tigrbl to construct (engine, session_factory)."""
    m = dict(mapping or {})
    url = dsn or m.get("url") or m.get("dsn") or kwargs.get("url")
    host = m.get("host") or kwargs.get("host")
    port = m.get("port") or kwargs.get("port")
    db = m.get("db") or kwargs.get("db")
    engine = RedisEngine(url=url, host=host, port=port, db=db, **kwargs)

    def session_factory() -> RedisSession:
        # Let the session lazily create the redis client
        return RedisSession(engine)

    return engine, session_factory
