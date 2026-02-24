"""Legacy handler argument resolution removed from ingress."""

from __future__ import annotations


async def resolve_handler_kwargs(*args, **kwargs):
    del args, kwargs
    raise RuntimeError(
        "Legacy handler argument resolution has been removed from ingress."
    )


__all__ = ["resolve_handler_kwargs"]
