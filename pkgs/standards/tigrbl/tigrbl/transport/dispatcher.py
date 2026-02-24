from __future__ import annotations


def dispatch_operation(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy operation dispatcher has been removed from ingress.")


def resolve_operation(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy operation dispatcher has been removed from ingress.")


__all__ = ["dispatch_operation", "resolve_operation"]
