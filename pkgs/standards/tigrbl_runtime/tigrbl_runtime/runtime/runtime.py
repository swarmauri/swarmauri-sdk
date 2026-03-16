from __future__ import annotations

from typing import Any

from tigrbl_kernel import Kernel, _default_kernel

from tigrbl_runtime.executors import ExecutorBase, PackedPlanExecutor
from .base import RuntimeBase


class Runtime(RuntimeBase):
    """Runtime orchestrator for kernel + executors."""

    def __init__(
        self,
        kernel: Kernel | None = None,
        *,
        default_executor: str = "packed",
    ) -> None:
        super().__init__(kernel=kernel or _default_kernel)
        self.default_executor = default_executor
        self.register_executor(PackedPlanExecutor())

    def register_executor(self, executor: ExecutorBase) -> None:
        executor.attach_runtime(self)
        self.executors[executor.name] = executor

    def compile(self, *args: Any, **kwargs: Any) -> tuple[Any, Any | None]:
        if args:
            app = args[0]
        else:
            app = kwargs.get("app")
        if app is None:
            raise ValueError("Runtime.compile requires an app instance")
        plan = self.kernel.kernel_plan(app)
        packed_plan = getattr(plan, "packed", None)
        return plan, packed_plan

    async def invoke(
        self,
        *,
        executor: str | None = None,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        selected = executor or self.default_executor
        impl = self.executors.get(selected)
        if impl is None:
            raise KeyError(f"Unknown executor: {selected}")
        return await impl.invoke(
            runtime=self,
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )


__all__ = ["Runtime"]
