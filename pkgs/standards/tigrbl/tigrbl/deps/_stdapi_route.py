"""Compatibility re-exports for API route primitives."""

from __future__ import annotations

from ..api._route import Handler, Route, compile_path

_compile_path = compile_path

__all__ = ["Handler", "Route", "compile_path", "_compile_path"]
