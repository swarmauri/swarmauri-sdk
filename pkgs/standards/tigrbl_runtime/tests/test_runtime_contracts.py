from tigrbl_runtime.executors import (
    ExecutorBase,
    NumbaPackedPlanExecutor,
    PackedPlanExecutor,
)
from tigrbl_runtime.runtime import Runtime, RuntimeBase


def test_runtime_and_executor_contracts_available() -> None:
    assert issubclass(Runtime, RuntimeBase)
    assert issubclass(PackedPlanExecutor, ExecutorBase)
    assert issubclass(NumbaPackedPlanExecutor, ExecutorBase)


def test_runtime_registers_default_executors() -> None:
    runtime = Runtime()
    assert set(runtime.executors) == {"packed", "numba_packed"}


def test_runtime_attaches_self_to_executors() -> None:
    runtime = Runtime()
    assert runtime.executors["packed"].runtime is runtime
    assert runtime.executors["numba_packed"].runtime is runtime


def test_runtime_default_executor_is_numba_packed() -> None:
    runtime = Runtime()
    assert runtime.default_executor == "numba_packed"
