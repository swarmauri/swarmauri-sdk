"""Deprecated ORM module wrapper.

Importing from :mod:`peagen.models` will be removed in a future release.
Use :mod:`peagen.orm` instead.
"""

from __future__ import annotations

import warnings

from peagen.orm import *  # noqa: F401,F403
from peagen.orm import Task as _Task

Task = _Task

__all__ = list(globals().get("__all__", []))
__all__.append("Task")

warnings.warn(
    "peagen.models is deprecated; use peagen.orm instead",
    DeprecationWarning,
    stacklevel=2,
)
