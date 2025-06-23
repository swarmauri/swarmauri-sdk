"""Expose core submodules at package level for testing convenience."""

from importlib import import_module as _import_module

doe_core = _import_module(".doe_core", __name__)

__all__ = ["doe_core"]
