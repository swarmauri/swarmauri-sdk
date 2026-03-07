from __future__ import annotations

from typing import Final, Tuple, Type


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


Stage = Type[object]

STAGES: Final[Tuple[Stage, ...]] = (
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

_STAGE_ORDINAL: Final[dict[Stage, int]] = {
    stage: idx for idx, stage in enumerate(STAGES)
}


def stage_name(stage: Stage) -> str:
    return stage.__name__


def stage_ordinal(stage: Stage) -> int:
    try:
        return _STAGE_ORDINAL[stage]
    except KeyError as e:
        raise ValueError(f"unknown stage: {stage!r}") from e


def is_valid_stage(stage: object) -> bool:
    return stage in _STAGE_ORDINAL


def is_monotonic_transition(src: Stage, dst: Stage) -> bool:
    if src is Failed or dst is Failed:
        return True
    return stage_ordinal(src) <= stage_ordinal(dst)


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
    "Stage",
    "STAGES",
    "stage_name",
    "stage_ordinal",
    "is_valid_stage",
    "is_monotonic_transition",
]