from __future__ import annotations

import inspect
import warnings
from types import SimpleNamespace
from typing import Any, Iterable

from sqlalchemy import text


def table_iter(router: Any) -> Iterable[type]:
    tables = getattr(router, "tables", None)
    if isinstance(tables, dict) and tables:
        return tables.values()

    return ()


def model_iter(router: Any) -> Iterable[type]:
    warnings.warn(
        "model_iter is deprecated; use table_iter instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return table_iter(router)


def opspecs(model: type):
    return getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()


def label_callable(fn: Any) -> str:
    n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    m = getattr(fn, "__module__", None)
    return f"{m}.{n}" if m else n


def label_hook(fn: Any, phase: str) -> str:
    label = getattr(fn, "__tigrbl_label", None)
    if isinstance(label, str):
        return label
    module = getattr(fn, "__module__", "") or ""
    name = getattr(fn, "__name__", "") or ""
    if module.startswith("tigrbl.core.crud") and name:
        return f"hook:wire:tigrbl:core:crud:ops:{name}@{phase}"
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
