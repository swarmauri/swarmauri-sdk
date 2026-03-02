from __future__ import annotations

import inspect
import warnings
from types import SimpleNamespace
from typing import Any, Iterable

from sqlalchemy import text

from ...runtime.labels import (
    label_callable as _kernel_label_callable,
    label_hook as _kernel_label_hook,
)


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


def label_callable(fn: Any) -> str:
    return _kernel_label_callable(fn)


def label_hook(fn: Any, phase: str) -> str:
    return _kernel_label_hook(fn, phase)
