<<<<<<<< HEAD:pkgs/standards/peagen/peagen/jsonschemas/__init__.py
# peagen/jsonschemas/__init__.py
"""Expose Peagen JSON Schemas as Python dicts."""
========
"""Deprecated access point for JSON Schemas."""
>>>>>>>> coby/peagenv2-add_schemas_06_25_25:pkgs/standards/peagen/peagen/schemas/__init__.py

from __future__ import annotations

import warnings

from peagen.jsonschemas import *  # noqa: F401,F403

warnings.warn(
    "peagen.schemas is deprecated; use peagen.jsonschemas instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [name for name in globals() if name.isupper()]
