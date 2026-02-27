# tigrbl/v3/ops/types.py
from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Literal, Tuple, cast

from ..config.constants import CANON as CANONICAL_VERB_TUPLE
from .._spec.op_spec import OpSpec


class PHASE(str, Enum):
    PRE_TX_BEGIN = "PRE_TX_BEGIN"
    START_TX = "START_TX"
    PRE_HANDLER = "PRE_HANDLER"
    HANDLER = "HANDLER"
    POST_HANDLER = "POST_HANDLER"
    PRE_COMMIT = "PRE_COMMIT"
    END_TX = "END_TX"
    POST_COMMIT = "POST_COMMIT"
    POST_RESPONSE = "POST_RESPONSE"
    ON_ERROR = "ON_ERROR"
    ON_PRE_TX_BEGIN_ERROR = "ON_PRE_TX_BEGIN_ERROR"
    ON_START_TX_ERROR = "ON_START_TX_ERROR"
    ON_PRE_HANDLER_ERROR = "ON_PRE_HANDLER_ERROR"
    ON_HANDLER_ERROR = "ON_HANDLER_ERROR"
    ON_POST_HANDLER_ERROR = "ON_POST_HANDLER_ERROR"
    ON_PRE_COMMIT_ERROR = "ON_PRE_COMMIT_ERROR"
    ON_END_TX_ERROR = "ON_END_TX_ERROR"
    ON_POST_COMMIT_ERROR = "ON_POST_COMMIT_ERROR"
    ON_POST_RESPONSE_ERROR = "ON_POST_RESPONSE_ERROR"
    ON_ROLLBACK = "ON_ROLLBACK"


HookPhase = Literal[
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "END_TX",
    "POST_COMMIT",
    "POST_RESPONSE",
    "ON_ERROR",
    "ON_PRE_TX_BEGIN_ERROR",
    "ON_START_TX_ERROR",
    "ON_PRE_HANDLER_ERROR",
    "ON_HANDLER_ERROR",
    "ON_POST_HANDLER_ERROR",
    "ON_PRE_COMMIT_ERROR",
    "ON_END_TX_ERROR",
    "ON_POST_COMMIT_ERROR",
    "ON_POST_RESPONSE_ERROR",
    "ON_ROLLBACK",
]
PHASES: Tuple[HookPhase, ...] = cast(
    Tuple[HookPhase, ...], tuple(p.value for p in PHASE)
)
Ctx = Any
StepFn = Callable[[Ctx], Any]
HookPredicate = Callable[[Any], bool]
EngineCfg = Any
OpHook = Any

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
