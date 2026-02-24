from .engine import ClickHouseEngine, clickhouse_engine
from .session import ClickHouseSession


def register() -> None:
    """Entry-point hook invoked by tigrbl to register the engine kind."""
    try:
        from tigrbl.engine.registry import register_engine
    except Exception:  # pragma: no cover
        from tigrbl.engine import register_engine  # type: ignore
    register_engine("clickhouse", clickhouse_engine)


__all__ = [
    "ClickHouseEngine",
    "ClickHouseSession",
    "clickhouse_engine",
    "register",
]
