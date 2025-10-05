from __future__ import annotations
from typing import Any, Callable, Tuple, Optional, Dict
from pyspark.sql import SparkSession

def pyspark_engine(
    app_name: str = "tigrbl-pyspark",
    conf: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> Tuple[Any, Callable[[], Any]]:
    """Build the underlying SparkSession and return (engine, session_factory)."""
    builder = SparkSession.builder.appName(app_name)
    for k, v in (conf or {}).items():
        builder = builder.config(k, v)
    spark = builder.getOrCreate()

    class _SessionHandle:
        """Thin wrapper exposing .close() and delegating to SparkSession."""
        def __init__(self, spark_session: SparkSession) -> None:
            self.spark = spark_session
        def close(self) -> None:
            # No-op by default; allow the application to manage lifecycle.
            pass
        def __getattr__(self, name: str) -> Any:
            return getattr(self.spark, name)

    def session_factory() -> _SessionHandle:
        return _SessionHandle(spark)

    return spark, session_factory

def pyspark_capabilities() -> dict:
    return {
        "sql": True,
        "dataframe": True,
        "transactions": False,
        "distributed": True,
        "dialect": "spark-sql",
    }
