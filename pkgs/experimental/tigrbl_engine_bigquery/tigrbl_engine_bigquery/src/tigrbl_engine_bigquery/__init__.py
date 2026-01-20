from .engine import BigQueryEngine, bigquery_engine
from .session import BigQuerySession


def register() -> None:
    """Entry point hook invoked by tigrbl to register the engine kind."""
    try:
        # Preferred path in the current tigrbl
        from tigrbl.engine.registry import register_engine
    except Exception:  # pragma: no cover
        # Fallback, in case of older packaging
        from tigrbl.engine import register_engine  # type: ignore
    # Register the builder under kind='bigquery'
    register_engine("bigquery", bigquery_engine)


__all__ = [
    "BigQueryEngine",
    "BigQuerySession",
    "bigquery_engine",
    "register",
]
