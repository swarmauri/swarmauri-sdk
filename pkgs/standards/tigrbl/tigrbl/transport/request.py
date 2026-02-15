"""Backward-compatible request exports.

Prefer importing from ``tigrbl.requests``.
"""

from tigrbl.headers import Headers
from tigrbl.requests._request import AwaitableValue, Request, URL

__all__ = ["Headers", "Request", "AwaitableValue", "URL"]
