"""Compatibility layer for Base moved to autoapi.v3.table."""

from __future__ import annotations

from ...table import Base
from ...table._base import _materialize_colspecs_to_sqla

__all__ = ["Base", "_materialize_colspecs_to_sqla"]
