from __future__ import annotations

from typing import Any

from tigrbl_kernel import Kernel, _default_kernel

from ..executors import ExecutorBase, PackedPlanExecutor, PhaseExecutor
from .base import RuntimeBase


class Runtime(RuntimeBase):
    """Runtime orchestrator for kernel + executors."""

    def __init__(self, kernel: Kernel | None = None) -> None:
        super().__init__(kernel=kernel or _default_kernel)
        self.register_executor("phase", PhaseExecutor())
        self.register_executor("packed", PackedPlanExecutor())

    def register_executor(self, name: str, executor: ExecutorBase) -> None:
        self.executors[name] = executor

    def compile(self, *args: Any, **kwargs: Any) -> tuple[Any, Any | None]:
        plan = self.kernel.compile(*args, **kwargs)
        packed_plan = self.kernel.pack(plan)
        return plan, packed_plan

    async def invoke(
        self,
        *,
        executor: str,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        impl = self.executors.get(executor)
        if impl is None:
            raise KeyError(f"Unknown executor: {executor}")
        return await impl.invoke(
            runtime=self,
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )


__all__ = ["Runtime"]
