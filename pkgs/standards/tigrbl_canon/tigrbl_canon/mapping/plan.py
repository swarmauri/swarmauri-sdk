from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Tuple

from .context import MappingContext
from .passes import bind_deps, bind_hooks, bind_models, bind_ops, collect, merge, seal


class Step(Enum):
    COLLECT = auto()
    MERGE = auto()
    BIND_MODELS = auto()
    BIND_OPS = auto()
    BIND_HOOKS = auto()
    BIND_DEPS = auto()
    SEAL = auto()


PlanFn = Callable[[MappingContext], MappingContext]


@dataclass(frozen=True)
class MappingPlan:
    steps: Tuple[tuple[Step, PlanFn], ...]

    def execute(self, ctx: MappingContext) -> MappingContext:
        for _, fn in self.steps:
            ctx = fn(ctx)
        return ctx


def compile_plan(*, deterministic: bool = True) -> MappingPlan:
    del deterministic
    return MappingPlan(
        steps=(
            (Step.COLLECT, collect),
            (Step.MERGE, merge),
            (Step.BIND_MODELS, bind_models),
            (Step.BIND_OPS, bind_ops),
            (Step.BIND_HOOKS, bind_hooks),
            (Step.BIND_DEPS, bind_deps),
            (Step.SEAL, seal),
        )
    )


def plan(context: MappingContext) -> MappingContext:
    """Compatibility wrapper around the compiled deterministic mapping plan."""
    return compile_plan().execute(context)


__all__ = ["Step", "MappingPlan", "compile_plan", "plan"]
