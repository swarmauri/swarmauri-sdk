"""Backward-compatible header primitive exports.

Transport header primitives now live under :mod:`tigrbl.transport`.
"""

from __future__ import annotations

from ..transport._header import HeaderCookies, Headers, SetCookieHeader

__all__ = ["Headers", "HeaderCookies", "SetCookieHeader"]
