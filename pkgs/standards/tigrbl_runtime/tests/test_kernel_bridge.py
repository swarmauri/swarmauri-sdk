from tigrbl_kernel import Kernel as KernelFromKernel

from tigrbl_runtime.runtime import Kernel as KernelFromRuntime
from tigrbl_runtime.executors.kernel_executor import KernelExecutor
from tigrbl_runtime.executors.packed import PackedPlanExecutor


def test_runtime_uses_kernel_class_from_tigrbl_kernel() -> None:
    assert KernelFromRuntime is KernelFromKernel


def test_runtime_attaches_executor_methods_to_kernel() -> None:
    assert KernelFromRuntime._run.__name__ == KernelExecutor._run.__name__
    assert (
        KernelFromRuntime._run_phase_chain.__name__
        == KernelExecutor._run_phase_chain.__name__
    )
    assert (
        KernelFromRuntime._run_segment_python.__name__
        == KernelExecutor._run_segment_python.__name__
    )
    assert KernelFromRuntime._coerce_int is PackedPlanExecutor._coerce_int
    assert (
        KernelFromRuntime._require_program_id_from_ctx.__name__
        == PackedPlanExecutor._require_program_id_from_ctx.__name__
    )
    assert (
        KernelFromRuntime._execute_packed.__name__
        == PackedPlanExecutor._execute_packed.__name__
    )
    assert (
        KernelFromRuntime._build_python_packed_executor
        is PackedPlanExecutor._build_python_packed_executor
    )
    assert (
        KernelFromRuntime._build_numba_packed_executor
        is PackedPlanExecutor._build_numba_packed_executor
    )
