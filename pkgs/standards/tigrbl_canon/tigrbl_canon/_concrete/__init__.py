"""Compatibility bridge to ``tigrbl_concrete._concrete`` modules."""

from importlib import import_module

_TARGET = "tigrbl_concrete._concrete"


def __getattr__(name: str):
    return import_module(f"{_TARGET}.{name}")
