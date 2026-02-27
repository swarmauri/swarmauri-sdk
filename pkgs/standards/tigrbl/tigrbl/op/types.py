# tigrbl/v3/ops/types.py
from __future__ import annotations

from typing import Literal, Tuple, cast

from ..config.constants import CANON as CANONICAL_VERB_TUPLE
from ..hook.types import PHASE, HookPhase, PHASES, Ctx, StepFn, HookPredicate
from ..hook import HookSpec as OpHook
from .._spec.engine_spec import EngineCfg
from .._spec.op_spec import OpSpec

# ───────────────────────────────────────────────────────────────────────────────
# Core aliases & enums
# ───────────────────────────────────────────────────────────────────────────────

PersistPolicy = Literal[
    "default",
    "prepend",
    "append",
    "override",
    "skip",
]  # TX policy
Arity = Literal["collection", "member"]  # HTTP path shape

TargetOp = Literal[
    "create",
    "read",
    "update",
    "replace",
    "merge",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
    "custom",
]

VerbAliasPolicy = Literal["both", "alias_only", "canonical_only"]  # legacy export

# Canonical verb set
CANON: Tuple[TargetOp, ...] = cast(Tuple[TargetOp, ...], CANONICAL_VERB_TUPLE)

__all__ = [
    "PersistPolicy",
    "Arity",
    "TargetOp",
    "VerbAliasPolicy",
    "PHASE",
    "HookPhase",
    "PHASES",
    "Ctx",
    "StepFn",
    "HookPredicate",
    "EngineCfg",
    "OpHook",
    "OpSpec",
    "CANON",
]
