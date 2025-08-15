"""Utility helpers for naming conventions.

This module centralizes helpers for converting between naming styles,
constructing canonical operation identifiers, and labeling callables.
"""

from __future__ import annotations

import re
from typing import Any

# will be removed with we remove verb op policy in place of opsec
VALID_VERBS = {
    "create",
    "read",
    "update",
    "delete",
    "list",
    "clear",
    "replace",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
}

# will be removed with we remove verb op policy in place of opsec
_alias_re = re.compile(r"^[a-z][a-z0-9_]*$")


def get_verb_alias_map(model) -> dict[str, str]:
    print("deprecating - use opspec")
    raw = getattr(model, "__autoapi_verb_aliases__", None)
    if callable(raw):
        raw = raw()
    return dict(raw or {})


def alias_policy(model) -> str:
    print("deprecating - use opspec")
    return getattr(model, "__autoapi_verb_alias_policy__", "both")


def public_verb(model, canonical: str) -> str:
    print("deprecating - use opspec")
    ali = get_verb_alias_map(model).get(canonical)
    if not ali or ali == canonical:
        return canonical
    if canonical not in VALID_VERBS:
        raise RuntimeError(f"{model.__name__}: unsupported verb {canonical!r}")
    if not _alias_re.match(ali):
        raise RuntimeError(
            f"{model.__name__}.__autoapi_verb_aliases__: bad alias {ali!r} for {canonical!r} "
            "(must be lowercase [a-z0-9_], start with a letter)"
        )
    return ali


def camel_to_snake(name: str) -> str:
    """Convert ``CamelCase`` *name* to ``snake_case`` preserving acronyms."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """Convert ``snake_case`` *name* to ``PascalCase``."""
    return "".join(w.title() for w in name.split("_")) if name.islower() else name


def canonical_name(resource: str, verb: str) -> str:
    """Return the canonical RPC method name for *resource* and *verb*."""
    cls_name = snake_to_camel(resource)
    name = f"{cls_name}.{verb}"
    print(f"_canonical generated {name}")
    return name


def resource_pascal(resource: str) -> str:
    """Return ``PascalCase`` form of *resource*."""
    return snake_to_camel(resource)


def route_label(
    resource_name: str, verb: str, alias_policy: str, public_verb: str
) -> str:
    """Return '{Resource} - {verb/alias}' per policy."""
    if alias_policy == "alias_only" and public_verb != verb:
        lab = public_verb
    elif alias_policy == "both" and public_verb != verb:
        lab = f"{verb}/{public_verb}"
    else:
        lab = verb
    return f"{resource_pascal(resource_name)} - {lab}"


def label_hook_callable(fn: Any) -> str:
    """Return a module-qualified label for *fn* suitable for hook listings."""
    n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    m = getattr(fn, "__module__", None)
    return f"{m}.{n}" if m else n


__all__ = [
    "camel_to_snake",
    "snake_to_camel",
    "canonical_name",
    "resource_pascal",
    "route_label",
    "label_hook_callable",
    "VALID_VERBS",
    "get_verb_alias_map",
    "alias_policy",
    "public_verb",
]
