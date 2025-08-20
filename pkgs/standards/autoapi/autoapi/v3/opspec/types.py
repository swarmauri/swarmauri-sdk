# autoapi/v3/opspec/types.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)

# ───────────────────────────────────────────────────────────────────────────────
# Core aliases & enums
# ───────────────────────────────────────────────────────────────────────────────

PersistPolicy = Literal["default", "skip", "override"]  # TX policy
Arity = Literal["collection", "member"]  # HTTP path shape

TargetOp = Literal[
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
    "custom",
]

VerbAliasPolicy = Literal["both", "alias_only", "canonical_only"]  # legacy export

# ───────────────────────────────────────────────────────────────────────────────
# Runtime phases (align with runtime/executor.py)
# ───────────────────────────────────────────────────────────────────────────────

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

PHASES: Tuple[HookPhase, ...] = (
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
)

# ───────────────────────────────────────────────────────────────────────────────
# Hook/handler function types
# ───────────────────────────────────────────────────────────────────────────────

Ctx = Any
StepFn = Callable[[Ctx], Union[Any, Awaitable[Any]]]
HookPredicate = Callable[[Any], bool]

# ───────────────────────────────────────────────────────────────────────────────
# Lazy-capable schema argument types
# ───────────────────────────────────────────────────────────────────────────────

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


SchemaKind = Literal["in", "out"]


@dataclass(frozen=True, slots=True)
class SchemaRef:
    """Lazy reference to `model.schemas.<alias>.(in_|out)`."""

    alias: str
    kind: SchemaKind = "in"


SchemaArg = Union[
    Type[BaseModel],  # direct Pydantic model
    SchemaRef,  # cross-op reference
    str,  # "alias.in" | "alias.out"
    Callable[[type], Type[BaseModel]],  # lambda cls: cls.schemas.create.in_
]

# ───────────────────────────────────────────────────────────────────────────────
# Hook & Spec dataclasses
# ───────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class OpHook:
    phase: HookPhase
    fn: StepFn
    order: int = 0
    when: Optional[HookPredicate] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True, slots=True)
class OpSpec:
    """
    Single source of truth for an operation.

    • `target` = canonical verb ("create"…,"custom")
    • `arity`  = REST shape ("member"|"collection")

    Serialization mode is inferred **only** from schema presence:
      - if model.schemas.<alias>.out exists → serialize
      - otherwise → raw pass-through
    """

    # Identity & exposure
    alias: str
    target: TargetOp
    table: Optional[type] = None
    expose_routes: bool = True
    expose_rpc: bool = True
    expose_method: bool = True

    # HTTP behavior
    arity: Arity = "collection"
    http_methods: Optional[Tuple[str, ...]] = None
    path_suffix: Optional[str] = None
    tags: Tuple[str, ...] = field(default_factory=tuple)

    # Persistence
    persist: PersistPolicy = "default"

    # Schema overrides (resolved later by binder)
    request_model: Optional[SchemaArg] = None
    response_model: Optional[SchemaArg] = None

    # Handler & hooks
    handler: Optional[StepFn] = None
    hooks: Tuple[OpHook, ...] = field(default_factory=tuple)

    # RBAC / diagnostics
    rbac_guard_op: Optional[str] = None
    core: Optional[StepFn] = None
    core_raw: Optional[StepFn] = None
    extra: Mapping[str, Any] = field(default_factory=dict)


# Canonical verb set
CANON: Tuple[TargetOp, ...] = (
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
    "custom",
)

__all__ = [
    "PersistPolicy",
    "Arity",
    "TargetOp",
    "VerbAliasPolicy",
    "HookPhase",
    "PHASES",
    "Ctx",
    "StepFn",
    "HookPredicate",
    "SchemaKind",
    "SchemaRef",
    "SchemaArg",
    "OpHook",
    "OpSpec",
    "CANON",
]
