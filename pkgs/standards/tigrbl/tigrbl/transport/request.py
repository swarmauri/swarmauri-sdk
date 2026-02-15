"""Backward-compatible request exports.

Prefer importing from ``tigrbl.requests``.
"""

from tigrbl.requests._request import AwaitableValue, Request, URL

__all__ = ["Request", "AwaitableValue", "URL"]
