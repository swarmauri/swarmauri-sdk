from __future__ import annotations

from warnings import warn

from tigrbl_concrete._mapping.rpc import register_and_attach, rpc_call

warn(
    "tigrbl_canon.mapping.rpc is deprecated; use tigrbl_concrete._mapping.rpc",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["register_and_attach", "rpc_call"]
