from __future__ import annotations

from tigrbl.engine.registry import register_engine
from .duck_builder import duckdb_engine, duckdb_capabilities


def register() -> None:
    # Entry point hook, called by Tigrbl's plugin loader.
    # Registers the 'duckdb' engine kind.
    register_engine("duckdb", duckdb_engine, duckdb_capabilities)
