"""Compatibility wrapper for runtime kernel APIs.

Canonical kernel planning now lives in ``tigrbl_kernel``.
Runtime execution stays in ``tigrbl_runtime.runtime.executor``.
"""

from ._executor import (
    _build_numba_packed_executor,
    _build_python_packed_executor,
    _coerce_int,
    _execute_packed,
    _require_program_id_from_ctx,
    _run,
    _run_phase_chain,
    _run_segment_python,
)

from tigrbl_kernel import (
    Kernel,
    _default_kernel,
    build_phase_chains,
    get_cached_specs,
    plan_labels,
)

__all__ = [
    "Kernel",
    "get_cached_specs",
    "_default_kernel",
    "build_phase_chains",
    "plan_labels",
]


Kernel._run = _run
Kernel._run_phase_chain = _run_phase_chain
Kernel._run_segment_python = _run_segment_python
Kernel._coerce_int = staticmethod(_coerce_int)
Kernel._require_program_id_from_ctx = _require_program_id_from_ctx
Kernel._execute_packed = _execute_packed
Kernel._build_python_packed_executor = _build_python_packed_executor
Kernel._build_numba_packed_executor = _build_numba_packed_executor
