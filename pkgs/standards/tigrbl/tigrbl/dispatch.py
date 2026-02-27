from __future__ import annotations


async def dispatch_operation(*args, **kwargs):
    del args, kwargs
    raise RuntimeError(
        "Operation dispatch is runtime-owned and only available via ASGI gateway ingress."
    )


def resolve_operation(*args, **kwargs):
    del args, kwargs
    raise RuntimeError(
        "Operation resolution is runtime-owned and only available via ASGI gateway ingress."
    )


__all__ = ["dispatch_operation", "resolve_operation"]
