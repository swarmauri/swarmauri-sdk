"""Compatibility wrapper for runtime kernel APIs.

Canonical kernel build/planning/execution now lives in ``tigrbl_kernel``.
"""

from tigrbl_kernel import (
    Kernel,
    _default_kernel,
    build_phase_chains,
    get_cached_specs,
    plan_labels,
    run,
)

__all__ = [
    "Kernel",
    "get_cached_specs",
    "_default_kernel",
    "build_phase_chains",
    "plan_labels",
    "run",
]
