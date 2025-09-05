from __future__ import annotations

import datetime as dt

from ...specs import IO
from ...types import UUID


def tzutcnow() -> dt.datetime:
    """Return an aware UTC ``datetime``."""
    return dt.datetime.now(dt.timezone.utc)


def tzutcnow_plus_day() -> dt.datetime:
    """Return an aware UTC ``datetime`` one day in the future."""
    return tzutcnow() + dt.timedelta(days=1)


def _infer_schema(cls, default: str = "public") -> str:
    """Extract schema from ``__table_args__`` in dict or tuple/list form."""
    args = getattr(cls, "__table_args__", None)
    if not args:
        return default
    if isinstance(args, dict):
        return args.get("schema", default)
    if isinstance(args, (tuple, list)):
        for elem in args:
            if isinstance(elem, dict) and "schema" in elem:
                return elem["schema"]
    return default


uuid_example = UUID("00000000-dead-beef-cafe-000000000000")

CRUD_IN = ("create", "update", "replace")
CRUD_OUT = ("read", "list")
CRUD_IO = IO(in_verbs=CRUD_IN, out_verbs=CRUD_OUT, mutable_verbs=CRUD_IN)
RO_IO = IO(out_verbs=CRUD_OUT)

__all__ = [
    "tzutcnow",
    "tzutcnow_plus_day",
    "_infer_schema",
    "uuid_example",
    "CRUD_IN",
    "CRUD_OUT",
    "CRUD_IO",
    "RO_IO",
]
