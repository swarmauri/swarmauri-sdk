from .engine import NumpyEngine, numpy_capabilities, numpy_engine
from .session import NumpySession


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return numpy_engine(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return numpy_capabilities()


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("numpy", _Registration())


__all__ = [
    "NumpyEngine",
    "NumpySession",
    "numpy_engine",
    "numpy_capabilities",
    "register",
]
