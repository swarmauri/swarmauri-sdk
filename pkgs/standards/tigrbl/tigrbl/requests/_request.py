"""Backward-compatible request model exports.

Transport primitives now live under :mod:`tigrbl.transport`.
"""

from __future__ import annotations

from ..transport._request import AwaitableValue, Request, URL

__all__ = ["AwaitableValue", "Request", "URL"]
