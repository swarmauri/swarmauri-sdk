from __future__ import annotations

from warnings import warn

from tigrbl_base._base._rest_map import *  # noqa: F403

warn(
    "tigrbl_concrete._mapping.rest.helpers is deprecated; use tigrbl_base._base._rest_map",
    DeprecationWarning,
    stacklevel=2,
)
