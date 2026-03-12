from tigrbl_kernel import Kernel as KernelFromKernel

from tigrbl_runtime.runtime import Kernel as KernelFromRuntime
from tigrbl_runtime.executors.kernel_executor import _run, _run_phase_chain


def test_runtime_uses_kernel_class_from_tigrbl_kernel() -> None:
    assert KernelFromRuntime is KernelFromKernel


def test_runtime_attaches_executor_methods_to_kernel() -> None:
    assert KernelFromRuntime._run is _run
    assert KernelFromRuntime._run_phase_chain is _run_phase_chain
