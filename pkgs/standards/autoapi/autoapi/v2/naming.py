"""Utility helpers for naming conventions.

This module centralizes helpers for converting between naming styles,
constructing canonical operation identifiers, and labeling callables.
"""

from __future__ import annotations

import re
from typing import Any


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
