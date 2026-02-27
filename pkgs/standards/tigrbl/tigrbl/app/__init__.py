"""Application-layer public API for Tigrbl."""

from __future__ import annotations

import warnings

from ..specs.app_spec import AppSpec

warnings.warn(
    "tigrbl.app.AppSpec is deprecated; import AppSpec from tigrbl.specs instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["AppSpec"]
