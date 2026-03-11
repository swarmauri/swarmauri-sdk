from tigrbl_kernel import Kernel as KernelFromKernel

from tigrbl_runtime.runtime import Kernel as KernelFromRuntime
from tigrbl_runtime.executors.kernel_executor import (
    _build_numba_packed_executor,
    _build_python_packed_executor,
    _coerce_int,
    _execute_packed,
    _require_program_id_from_ctx,
    _run,
    _run_phase_chain,
    _run_segment_python,
)


def test_runtime_uses_kernel_class_from_tigrbl_kernel() -> None:
    assert KernelFromRuntime is KernelFromKernel


def test_runtime_attaches_executor_methods_to_kernel() -> None:
    assert KernelFromRuntime._run is _run
    assert KernelFromRuntime._run_phase_chain is _run_phase_chain
    assert KernelFromRuntime._run_segment_python is _run_segment_python
    assert KernelFromRuntime._coerce_int is _coerce_int
    assert (
        KernelFromRuntime._require_program_id_from_ctx is _require_program_id_from_ctx
    )
    assert KernelFromRuntime._execute_packed is _execute_packed
    assert (
        KernelFromRuntime._build_python_packed_executor is _build_python_packed_executor
    )
    assert (
        KernelFromRuntime._build_numba_packed_executor is _build_numba_packed_executor
    )
