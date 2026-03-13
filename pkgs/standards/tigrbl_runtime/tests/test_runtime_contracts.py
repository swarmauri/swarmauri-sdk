from tigrbl_runtime.executors import ExecutorBase, PackedPlanExecutor, PhaseExecutor
from tigrbl_runtime.runtime import Runtime, RuntimeBase


def test_runtime_and_executor_contracts_available() -> None:
    assert issubclass(Runtime, RuntimeBase)
    assert issubclass(PhaseExecutor, ExecutorBase)
    assert issubclass(PackedPlanExecutor, ExecutorBase)


def test_runtime_registers_default_executors() -> None:
    runtime = Runtime()
    assert set(runtime.executors) >= {"phase", "packed"}


def test_runtime_attaches_self_to_executors() -> None:
    runtime = Runtime()
    assert runtime.executors["phase"].runtime is runtime
    assert runtime.executors["packed"].runtime is runtime


def test_runtime_default_executor_is_packed() -> None:
    runtime = Runtime()
    assert runtime.default_executor == "packed"
