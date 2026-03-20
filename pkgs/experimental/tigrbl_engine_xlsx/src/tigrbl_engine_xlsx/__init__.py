from .engine import WorkbookCatalog, XlsxEngine, xlsx_capabilities, xlsx_engine
from .session import XlsxSession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return xlsx_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return xlsx_capabilities()


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("xlsx", _Registration())


__all__ = [
    "WorkbookCatalog",
    "XlsxEngine",
    "XlsxSession",
    "xlsx_engine",
    "xlsx_capabilities",
    "register",
]
