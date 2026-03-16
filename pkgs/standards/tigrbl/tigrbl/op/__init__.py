"""Compatibility facade for op APIs across split tigrbl packages."""

import tigrbl_core.op as _core_op
from tigrbl_core.op import *  # noqa: F403
from tigrbl_core._spec.op_spec import resolve
from tigrbl_concrete._concrete._op_registry import (
    OpspecRegistry,
    clear_registry,
    get_registered_ops,
    get_registry,
    register_ops,
)

__all__ = [
    *_core_op.__all__,
    "OpspecRegistry",
    "get_registry",
    "register_ops",
    "get_registered_ops",
    "clear_registry",
    "resolve",
]
