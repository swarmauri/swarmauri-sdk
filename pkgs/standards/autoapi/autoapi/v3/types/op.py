"""
autoapi/v2/types/_op.py
Pure structural helpers (no FastAPI / DB imports).
"""

from typing import Any, Callable, NamedTuple, Type, Literal, TypeAlias

_SchemaVerb: TypeAlias = Literal[
    "create",
    "read",
    "update",
    "delete",
    "list",
    "clear",
]

# need to add clear
# need to add support for bulk create, update, delete


class _Op(NamedTuple):
    """
    Metadata for one REST/RPC operation registered by AutoAPI.
    """

    verb: str  # e.g. "create", "list"
    http: str  # "POST" | "GET" | "PATCH" | …
    path: str  # URL suffix, e.g. "/{item_id}"
    In: Type | None  # Pydantic input model (or None)
    Out: Type  # Pydantic output model
    core: Callable[..., Any]  # The actual implementation


__all__ = ["_Op", "_SchemaVerb"]
