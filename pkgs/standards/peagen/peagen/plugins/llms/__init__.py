"""Lazy loader for Swarmauri LLM implementations.

This module exposes the classes from ``swarmauri_standard.llms`` or
``swarmauri.llms`` as attributes so they can be registered as plugin
entry-points under ``peagen.plugins.llms``.
"""

from importlib import import_module
from typing import Any


def _load_llm_class(name: str) -> Any:
    """Import ``name`` from swarmauri LLM modules."""
    try:
        module = import_module(f"swarmauri_standard.llms.{name}")
    except ImportError:
        module = import_module(f"swarmauri.llms.{name}")
    return getattr(module, name)


def __getattr__(name: str) -> Any:  # pragma: no cover - thin wrapper
    cls = _load_llm_class(name)
    globals()[name] = cls
    return cls
