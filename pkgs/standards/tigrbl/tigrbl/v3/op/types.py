# tigrbl/v3/ops/types.py
from __future__ import annotations

from dataclasses import dataclass, field

from typing import Any, Literal, Mapping, Optional, Tuple, cast

from ..config.constants import CANON as CANONICAL_VERB_TUPLE
from ..hook.types import PHASE, HookPhase, PHASES, Ctx, StepFn, HookPredicate
from ..hook import HookSpec as OpHook
from ..response.types import ResponseSpec
from ..engine.engine_spec import EngineCfg
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..schema.types import SchemaArg
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

# ───────────────────────────────────────────────────────────────────────────────
# Lazy-capable schema argument types
# ───────────────────────────────────────────────────────────────────────────────


# ───────────────────────────────────────────────────────────────────────────────
# Engine binding (optional, used by resolver precedence: op > table > api > app)
# ───────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class OpSpec:
    """
    Single source of truth for an operation.

    • `target` = canonical verb ("create"…,"custom")
    • `arity`  = REST shape ("member"|"collection")

    Serialization mode is inferred **only** from schema presence:
      - if model.schemas.<alias>.out exists → serialize
      - otherwise → raw pass-through

    Optional engine binding:
      - `engine` allows per-op routing (DSN string or structured mapping).
        When present, it participates in resolver precedence (op > table > api > app).
    """

    # Identity & exposure
    alias: str
    target: TargetOp
    table: Optional[type] = None
    expose_routes: bool = True
    expose_rpc: bool = True
    expose_method: bool = True

    # Optional per-op engine binding (DSN string or mapping spec)
    engine: Optional[EngineCfg] = None

    # HTTP behavior
    arity: Arity = "collection"
    http_methods: Optional[Tuple[str, ...]] = None
    path_suffix: Optional[str] = None
    tags: Tuple[str, ...] = field(default_factory=tuple)
    status_code: Optional[int] = None
    response: Optional[ResponseSpec] = None

    # Persistence
    persist: PersistPolicy = "default"

    # Schema overrides (resolved later by binder)
    request_model: Optional[SchemaArg] = None
    response_model: Optional[SchemaArg] = None

    # Return shaping: "raw" passthrough vs "model" serialization
    returns: Literal["raw", "model"] = "raw"

    # Handler & hooks
    handler: Optional[StepFn] = None
    hooks: Tuple[OpHook, ...] = field(default_factory=tuple)

    # RBAC / diagnostics
    rbac_guard_op: Optional[str] = None
    core: Optional[StepFn] = None
    core_raw: Optional[StepFn] = None
    extra: Mapping[str, Any] = field(default_factory=dict)
    deps: Tuple[StepFn | str, ...] = field(default_factory=tuple)
    secdeps: Tuple[StepFn | str, ...] = field(default_factory=tuple)


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
