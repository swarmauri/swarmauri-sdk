# ── Third-party dependency re-exports (preferred namespace) ────────────────
"""Centralized third-party dependency imports for tigrbl.

Prefer importing from :mod:`tigrbl.vendor` to avoid naming collisions with
framework dependency-injection concepts.
"""

from typing import TYPE_CHECKING, Any

from .._concrete._route import Route, compile_path

if TYPE_CHECKING:
    from tigrbl import Router
else:
    Router = Any

from .sqlalchemy import relationship  # noqa: F401
from .sqlalchemy import *  # noqa: F403, F401
from .pydantic import *  # noqa: F403, F401

__all__ = ["Router", "Route", "compile_path"]
