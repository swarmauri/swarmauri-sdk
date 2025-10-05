from .engine import RedisEngine, redis_engine
from .session import RedisSession

def register() -> None:
    """Entry point hook invoked by tigrbl to register the engine kind."""
    try:
        from tigrbl.engine.registry import register_engine
    except Exception:  # pragma: no cover
        from tigrbl.engine import register_engine  # type: ignore
    register_engine("redis", redis_engine)

__all__ = [
    "RedisEngine",
    "RedisSession",
    "redis_engine",
    "register",
]
