from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Iterable

from sqlalchemy import text


def model_iter(api: Any) -> Iterable[type]:
    models = getattr(api, "models", {}) or {}
    return models.values()


def opspecs(model: type):
    """
    Return the sequence of OpSpecs for a model.

    Prefer the indexed ``model.opspecs.all`` populated by the high-level binder.
    When tests build per-concern bindings directly (schemas/hooks/handlers/rest/rpc)
    without calling the orchestrator, the index may be absent; in that case fall
    back to collecting ctx-decorated ops from the model's MRO so diagnostics and
    kernel priming still have visibility into available aliases.
    """
    seq = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()
    if seq:
        return seq
    try:
        from ...op.mro_collect import mro_collect_decorated_ops

        return tuple(mro_collect_decorated_ops(model))
    except Exception:
        return ()


def label_callable(fn: Any) -> str:
    n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    m = getattr(fn, "__module__", None)
    return f"{m}.{n}" if m else n


def label_hook(fn: Any, phase: str) -> str:
    label = getattr(fn, "__tigrbl_label", None)
    if isinstance(label, str):
        return label
    subj = label_callable(fn).replace(".", ":")
    return f"hook:wire:{subj}@{phase}"


async def maybe_execute(db: Any, stmt: str):
    try:
        rv = db.execute(text(stmt))  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv
    except Exception:
        rv = db.execute(text("select 1"))  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv
