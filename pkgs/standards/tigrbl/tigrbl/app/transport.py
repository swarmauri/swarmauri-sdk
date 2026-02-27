"""Compatibility wrappers for transport gateway adapters."""

from __future__ import annotations


def asgi_app(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy ASGI transport gateway has been removed from ingress.")


def wsgi_app(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy WSGI transport gateway has been removed from ingress.")


__all__ = ["asgi_app", "wsgi_app"]
