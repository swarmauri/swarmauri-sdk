"""Snowflake engine plugin for Tigrbl.

Exports:
- snowflake_engine(): builder used by Tigrbl's registry
- snowflake_capabilities(): optional capability metadata
- SnowflakeSession: SQLAlchemy Session alias
- register(): entry-point hook to register with Tigrbl

The package auto-registers via pyproject entry-points under group 'tigrbl.engine'.
"""
from __future__ import annotations

from .engine import snowflake_engine, snowflake_capabilities
from .session import SnowflakeSession

def register() -> None:
    # Late import to avoid importing tigrbl at module import-time
    from tigrbl.engine.registry import register_engine
    register_engine("snowflake", snowflake_engine, snowflake_capabilities)

__all__ = [
    "snowflake_engine",
    "snowflake_capabilities",
    "SnowflakeSession",
    "register",
]
