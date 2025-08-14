"""Utility helpers for AutoAPI naming conventions.

This module centralizes helpers that convert between common casing styles and
construct canonical names and labels used across the AutoAPI package.
"""

from __future__ import annotations

import re
from typing import Any


def camel_to_snake(name: str) -> str:
    """Convert ``CamelCase`` ``name`` to ``snake_case`` preserving acronyms."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_pascal(name: str) -> str:
    """Convert ``snake_case`` ``name`` to ``PascalCase``."""
    return "".join(word.title() for word in name.split("_"))


def resource_pascal(tab_or_cls: str) -> str:
    """Return ``tab_or_cls`` converted to ``PascalCase`` if needed."""
    return snake_to_pascal(tab_or_cls) if tab_or_cls.islower() else tab_or_cls


def canonical(tab: str, verb: str) -> str:
    """Return canonical RPC method name ``{Resource}.{verb}``."""
    cls_name = resource_pascal(tab)
    name = f"{cls_name}.{verb}"
    print(f"canonical generated {name}")
    return name


def route_label(
    resource_name: str, verb: str, alias_policy: str, public_verb: str
) -> str:
    """Return a label ``{Resource} - {verb/alias}`` based on alias policy."""
    if alias_policy == "alias_only" and public_verb != verb:
        lab = public_verb
    elif alias_policy == "both" and public_verb != verb:
        lab = f"{verb}/{public_verb}"
    else:
        lab = verb
    return f"{resource_pascal(resource_name)} - {lab}"


def label_hook_callable(fn: Any) -> str:
    """Return a fully qualified label for hook callable ``fn``."""
    n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    m = getattr(fn, "__module__", None)
    return f"{m}.{n}" if m else n
