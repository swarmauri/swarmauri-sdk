from __future__ import annotations
from typing import Any
from pyspark.sql import SparkSession


class PySparkSession:
    """Optional thin wrapper around SparkSession used by the plugin."""

    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def sql(self, query: str, *args: Any, **kwargs: Any):
        return self.spark.sql(query, *args, **kwargs)

    def close(self) -> None:
        # Intentionally a no-op by default. Users may stop the session explicitly if desired.
        pass
