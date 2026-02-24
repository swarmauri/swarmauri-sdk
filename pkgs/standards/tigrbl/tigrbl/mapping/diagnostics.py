from __future__ import annotations

from .context import MappingContext
from .plan import MappingPlan


def explain_plan(plan: MappingPlan) -> list[str]:
    return [step.name for step, _ in plan.steps]


def context_diff(
    before: MappingContext, after: MappingContext
) -> dict[str, tuple[object, object]]:
    diff: dict[str, tuple[object, object]] = {}
    for field in before.__dataclass_fields__:
        left = getattr(before, field)
        right = getattr(after, field)
        if left != right:
            diff[field] = (left, right)
    return diff
