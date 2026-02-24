from .engine import pyspark_engine, pyspark_capabilities
from .session import PySparkSession


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("pyspark", build=pyspark_engine, capabilities=pyspark_capabilities)


__all__ = [
    "pyspark_engine",
    "pyspark_capabilities",
    "PySparkSession",
    "register",
]
