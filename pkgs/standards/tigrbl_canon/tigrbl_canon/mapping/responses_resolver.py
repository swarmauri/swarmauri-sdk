from __future__ import annotations

from warnings import warn

from tigrbl_core._spec import resolve_response_spec
from tigrbl_runtime.runtime.response import infer_hints

warn(
    "tigrbl_canon.mapping.responses_resolver is deprecated; use tigrbl_core._spec.resolve_response_spec and tigrbl_runtime.runtime.response.infer_hints",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["resolve_response_spec", "infer_hints"]
