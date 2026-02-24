"""Legacy dependency execution façade removed from ingress."""

from __future__ import annotations


class DependencyToken:
    def __init__(self, *args, **kwargs) -> None:
        del args, kwargs
        raise RuntimeError("Legacy dependency token execution has been removed.")


async def execute_route_dependencies(*args, **kwargs) -> None:
    del args, kwargs
    raise RuntimeError("Legacy route dependency execution has been removed.")


async def execute_dependency_tokens(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy dependency token execution has been removed.")


async def invoke_dependency(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy dependency invocation has been removed.")


__all__ = [
    "DependencyToken",
    "invoke_dependency",
    "execute_route_dependencies",
    "execute_dependency_tokens",
]
