# tigrbl/v3/ops/types.py
from __future__ import annotations

from typing import Literal, Tuple, cast

from tigrbl_core._spec.hook_types import HookPhase, HookPhases, StepFn
from tigrbl_core._spec.op_spec import Arity, OpSpec, PersistPolicy, TargetOp
from tigrbl_core.config.constants import CANON as CANONICAL_VERB_TUPLE

# ───────────────────────────────────────────────────────────────────────────────
# Core aliases & enums
# ───────────────────────────────────────────────────────────────────────────────

VerbAliasPolicy = Literal["both", "alias_only", "canonical_only"]  # legacy export

# Canonical verb set
CANON: Tuple[TargetOp, ...] = cast(Tuple[TargetOp, ...], CANONICAL_VERB_TUPLE)

__all__ = [
    "PersistPolicy",
    "Arity",
    "TargetOp",
    "VerbAliasPolicy",
    "OpSpec",
    "HookPhase",
    "HookPhases",
    "StepFn",
    "CANON",
]
