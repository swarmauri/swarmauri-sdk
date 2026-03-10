from __future__ import annotations
from typing import Any, Dict
from types import SimpleNamespace

from . import kernel as _kernel  # single, app-scoped kernel


def _ensure_temp(ctx: Any) -> Dict[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def opview_from_ctx(ctx: Any):
    """
    Resolve the ``OpView`` for this request context or raise a runtime error.

    Preferred resolution path is via ``ctx.opview`` which should be attached by
    the caller.  Falling back to kernel lookups requires ``ctx.app`` (or
    ``ctx.router``), ``ctx.model`` (or derivable from ``ctx.obj``), and ``ctx.op``
    (or ``ctx.method``).
    """
    ov = getattr(ctx, "opview", None)
    if ov is not None:
        return ov

    app = getattr(ctx, "app", None) or getattr(ctx, "router", None)
    model = getattr(ctx, "model", None)
    if model is None:
        obj = getattr(ctx, "obj", None)
        if obj is not None:
            model = type(obj)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)

    if app and model and alias:
        # One-kernel-per-app, prime once; raises if not compiled
        return _kernel._default_kernel.get_opview(app, model, alias)

    if alias:
        specs = getattr(ctx, "specs", None)
        if specs is not None:
            return _kernel._default_kernel._compile_opview_from_specs(
                specs, SimpleNamespace(alias=alias)
            )

    missing = []
    if not alias:
        missing.append("op")
    if not app:
        missing.append("app")
    if not model:
        missing.append("model")
    # runtime-error policy: eject loudly; no skip
    raise RuntimeError(f"ctx_missing:{','.join(missing)}")


__all__ = ["opview_from_ctx", "_ensure_temp"]
