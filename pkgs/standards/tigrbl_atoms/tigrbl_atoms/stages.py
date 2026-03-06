
from __future__ import annotations

from typing import Final, Tuple, Type

"""
Stage markers for Tigrbl's typed execution algebra.

A stage is a typed invariant over ctx, not a lifecycle anchor.

Mainline progression:

    Boot
    -> Ingress
    -> Routed
    -> Bound
    -> Selected
    -> Authorized
    -> Executing
    -> Ready
    -> Operated
    -> Encoded
    -> Emitting
    -> Egressed

with failure transitions to:

    Failed
"""


class Boot: ...
class Ingress: ...
class Routed: ...
class Bound: ...
class Selected: ...
class Authorized: ...
class Executing: ...
class Ready: ...
class Operated: ...
class Encoded: ...
class Emitting: ...
class Egressed: ...
class Failed: ...


StageType = Type[object]

STAGES: Final[Tuple[StageType, ...]] = (
    Boot,
    Ingress,
    Routed,
    Bound,
    Selected,
    Authorized,
    Executing,
    Ready,
    Operated,
    Encoded,
    Emitting,
    Egressed,
    Failed,
)

_STAGE_ORDINAL = {stage: idx for idx, stage in enumerate(STAGES)}


def stage_name(stage: StageType) -> str:
    return stage.__name__


def stage_ordinal(stage: StageType) -> int:
    try:
        return _STAGE_ORDINAL[stage]
    except KeyError as e:
        raise ValueError(f"Unknown stage: {stage!r}") from e


def is_valid_stage(stage: StageType) -> bool:
    return stage in _STAGE_ORDINAL


def is_monotonic_transition(src: StageType, dst: StageType) -> bool:
    """
    True if src -> dst is forward-only in the mainline stage order.
    Failed is treated as terminal and exempt from normal forward checks.
    """
    if src is Failed or dst is Failed:
        return True
    return stage_ordinal(src) <= stage_ordinal(dst)


def order_stages(stages: tuple[StageType, ...] | list[StageType]) -> list[StageType]:
    out = list(stages)
    out.sort(key=stage_ordinal)
    return out


__all__ = [
    "Boot",
    "Ingress",
    "Routed",
    "Bound",
    "Selected",
    "Authorized",
    "Executing",
    "Ready",
    "Operated",
    "Encoded",
    "Emitting",
    "Egressed",
    "Failed",
    "StageType",
    "STAGES",
    "stage_name",
    "stage_ordinal",
    "is_valid_stage",
    "is_monotonic_transition",
    "order_stages",
]
