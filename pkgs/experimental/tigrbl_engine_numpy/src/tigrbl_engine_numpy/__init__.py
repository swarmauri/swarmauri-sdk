from .engine import NumpyEngine, numpy_capabilities, numpy_engine
from .session import NumpySession


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine("numpy", build=numpy_engine, capabilities=numpy_capabilities)


__all__ = [
    "NumpyEngine",
    "NumpySession",
    "numpy_engine",
    "numpy_capabilities",
    "register",
]
