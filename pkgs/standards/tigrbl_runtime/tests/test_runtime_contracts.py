from tigrbl_runtime.executors import ExecutorBase, PackedPlanExecutor, PhaseExecutor
from tigrbl_runtime.runtime import Runtime, RuntimeBase


def test_runtime_and_executor_contracts_available() -> None:
    assert issubclass(Runtime, RuntimeBase)
    assert issubclass(PhaseExecutor, ExecutorBase)
    assert issubclass(PackedPlanExecutor, ExecutorBase)


def test_runtime_registers_default_executors() -> None:
    runtime = Runtime()
    assert set(runtime.executors) >= {"phase", "packed"}
