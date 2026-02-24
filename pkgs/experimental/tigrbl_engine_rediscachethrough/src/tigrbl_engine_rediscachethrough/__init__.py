from .engine import rediscachethrough_engine, rediscachethrough_capabilities
from .session import CacheThroughSession


def register() -> None:
    """Entry-point hook invoked by tigrbl to register this engine."""
    from tigrbl.engine.registry import register_engine

    register_engine(
        "rediscachethrough",
        build=rediscachethrough_engine,
        capabilities=rediscachethrough_capabilities,
    )


__all__ = [
    "rediscachethrough_engine",
    "rediscachethrough_capabilities",
    "CacheThroughSession",
    "register",
]
