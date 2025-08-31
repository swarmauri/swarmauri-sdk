# autoapi/v3/specs/__init__.py
"""Compatibility layer that re-exports column specs.

Importing from ``autoapi.v3.specs`` remains supported but the
implementation now lives under :mod:`autoapi.v3.column`.
"""

from __future__ import annotations

from ..column import *  # noqa: F401,F403
from ..column import __all__ as _all

__all__ = list(_all)


def __dir__() -> list[str]:
    return sorted(__all__)
