# ── Third-party Dependencies Re-exports ─────────────────────────────────
"""
Centralized third-party dependency imports for tigrbl.

This module provides a single location for all third-party dependencies,
making it easier to manage versions and potential replacements.
"""

from ..router._api import APIRouter
from ..router._route import Route, compile_path
from ..router._router import Router

# Re-export all SQLAlchemy dependencies
from .sqlalchemy import relationship  # noqa: F401
from .sqlalchemy import *  # noqa: F403, F401

# Re-export all Pydantic dependencies
from .pydantic import *  # noqa: F403, F401

__all__ = [
    "APIRouter",
    "Router",
    "Route",
    "compile_path",
]
