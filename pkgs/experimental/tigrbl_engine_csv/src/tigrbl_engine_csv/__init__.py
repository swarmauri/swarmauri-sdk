from .engine import CsvEngine, csv_capabilities, csv_engine
from .session import CsvSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return csv_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return csv_capabilities()


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("csv", _Registration())


__all__ = [
    "CsvEngine",
    "CsvSession",
    "csv_engine",
    "csv_capabilities",
    "register",
]
