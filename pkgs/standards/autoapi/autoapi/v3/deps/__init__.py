# ── Third-party Dependencies Re-exports ─────────────────────────────────
"""
Centralized third-party dependency imports for autoapi.v3.

This module provides a single location for all third-party dependencies,
making it easier to manage versions and potential replacements.
"""

# Re-export all SQLAlchemy dependencies
from .sqlalchemy import *  # noqa: F403, F401

# Re-export all Pydantic dependencies
from .pydantic import *  # noqa: F403, F401

# Re-export all FastAPI dependencies
from .fastapi import *  # noqa: F403, F401

# Re-export all Starlette dependencies
from .starlette import *  # noqa: F403, F401
