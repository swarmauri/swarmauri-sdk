from __future__ import annotations

from warnings import warn

from tigrbl_base._base._rpc_map import *  # noqa: F403

warn(
    "tigrbl_concrete._mapping.rpc is deprecated; use tigrbl_base._base._rpc_map",
    DeprecationWarning,
    stacklevel=2,
)
