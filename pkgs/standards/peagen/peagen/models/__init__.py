"""Deprecated ORM module wrapper.

Importing from :mod:`peagen.models` will be removed in a future release.
Use :mod:`peagen.orm` instead.
"""

from __future__ import annotations

import warnings

from peagen.orm import *  # noqa: F401,F403
from peagen.orm.task.task import Task  # noqa: F401

__all__ = [name for name in globals() if not name.startswith("_")]

warnings.warn(
    "peagen.models is deprecated; use peagen.orm instead",
    DeprecationWarning,
    stacklevel=2,
)
