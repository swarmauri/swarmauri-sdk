from .engine import pyspark_capabilities, pyspark_engine
from .session import PySparkSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return pyspark_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return pyspark_capabilities()


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("pyspark", _Registration())


__all__ = [
    "pyspark_engine",
    "pyspark_capabilities",
    "PySparkSession",
    "register",
]
