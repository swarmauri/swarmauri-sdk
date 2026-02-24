"""Compatibility wrapper for response shortcuts.

Canonical shortcuts live under :mod:`tigrbl.shortcuts.responses`.
"""

from __future__ import annotations

from ..shortcuts.responses import (  # noqa: F401
    as_file,
    as_html,
    as_json,
    as_redirect,
    as_stream,
    as_text,
)

__all__ = [
    "as_json",
    "as_html",
    "as_text",
    "as_redirect",
    "as_stream",
    "as_file",
]
