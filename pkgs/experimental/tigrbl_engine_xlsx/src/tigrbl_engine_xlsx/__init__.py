from .engine import WorkbookCatalog, XlsxEngine, xlsx_capabilities, xlsx_engine
from .session import XlsxSession


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("xlsx", build=xlsx_engine, capabilities=xlsx_capabilities)


__all__ = [
    "WorkbookCatalog",
    "XlsxEngine",
    "XlsxSession",
    "xlsx_engine",
    "xlsx_capabilities",
    "register",
]
