"""Compatibility wrapper for runtime kernel APIs.

Canonical kernel planning now lives in ``tigrbl_kernel``.
Runtime execution stays in ``tigrbl_runtime.executors``.
"""

from ..executors.kernel_executor import KernelExecutor
from ..executors.packed import PackedPlanExecutor

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


_kernel_executor = KernelExecutor()
_packed_executor = PackedPlanExecutor()

Kernel._run = _kernel_executor._run
Kernel._run_phase_chain = _kernel_executor._run_phase_chain
Kernel._run_segment_python = _kernel_executor._run_segment_python
Kernel._coerce_int = staticmethod(PackedPlanExecutor._coerce_int)
Kernel._require_program_id_from_ctx = _packed_executor._require_program_id_from_ctx
Kernel._execute_packed = _packed_executor._execute_packed
Kernel._build_python_packed_executor = staticmethod(
    PackedPlanExecutor._build_python_packed_executor
)
Kernel._build_numba_packed_executor = staticmethod(
    PackedPlanExecutor._build_numba_packed_executor
)
