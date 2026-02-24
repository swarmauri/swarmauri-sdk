from .engine import CsvEngine, csv_capabilities, csv_engine
from .session import CsvSession


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("csv", build=csv_engine, capabilities=csv_capabilities)


__all__ = [
    "CsvEngine",
    "CsvSession",
    "csv_engine",
    "csv_capabilities",
    "register",
]
