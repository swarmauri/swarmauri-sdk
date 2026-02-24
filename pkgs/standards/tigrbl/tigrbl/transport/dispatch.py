from __future__ import annotations


def dispatch_operation(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy operation dispatch has been removed from ingress.")


def resolve_operation(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy operation resolution has been removed from ingress.")


def resolve_model(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy operation resolution has been removed from ingress.")


def resolve_target(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy operation resolution has been removed from ingress.")


def build_ctx(*args, **kwargs):
    del args, kwargs
    raise RuntimeError(
        "Legacy operation dispatch context has been removed from ingress."
    )


def build_phase_chains(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("Legacy operation phase chains have been removed from ingress.")


__all__ = [
    "dispatch_operation",
    "resolve_operation",
    "resolve_model",
    "resolve_target",
    "build_ctx",
    "build_phase_chains",
]
