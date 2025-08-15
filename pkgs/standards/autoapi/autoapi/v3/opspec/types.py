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

# Persistence policy for an op:
#  - "default": persistent op; binder auto-adds START_TX and END_TX hooks.
#  - "skip":    ephemeral; binder suppresses START_TX/END_TX and forbids writes.
#  - "override": persistent, but caller-provided hooks may override defaults.
PersistPolicy = Literal["default", "skip", "override"]

# HTTP path shape / id expectation
Arity = Literal["collection", "member"]

# Canonical targets + "custom" for user-defined ops
TargetOp = Literal[
    # canonical CRUD
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
    # bulk
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
    # custom
    "custom",
]

# Response serialization preference
ReturnForm = Literal["model", "raw"]

# Alias exposure policy for RPC/method helpers
VerbAliasPolicy = Literal["both", "alias_only", "canonical_only"]

# ───────────────────────────────────────────────────────────────────────────────
# Runtime phases (align with runtime/executor.py)
# ───────────────────────────────────────────────────────────────────────────────
# Flush-only: PRE_HANDLER, HANDLER, POST_HANDLER
# No writes:  PRE_COMMIT, POST_COMMIT
# Commit:     END_TX (commit allowed)
# Begin:      START_TX (begin-only)
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
    # error/rollback hooks
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

# An ordered, canonical listing some callers may want for UIs/validation
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

# Ctx-like object used at runtime; kept as Any to avoid importing executor internals here.
Ctx = Any

# A handler/hook step accepts a context and may return any value (used as ctx.result).
StepFn = Callable[[Ctx], Union[Any, Awaitable[Any]]]

# Optional predicate to conditionally enable a hook for a given payload/ctx
HookPredicate = Callable[[Any], bool]

# ───────────────────────────────────────────────────────────────────────────────
# Hook & Spec dataclasses
# ───────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class OpHook:
    """
    A single hook contribution for an OpSpec, inserted into the phase chain.

    • phase: one of HookPhase (see PHASES above)
    • fn: a StepFn(ctx) → Any | Awaitable[Any]
    • order: stable sort key within the phase (smaller runs earlier)
    • when: optional predicate(payload_or_ctx) → bool to include/skip dynamically
    • name/description: metadata for diagnostics / UIs
    """

    phase: HookPhase
    fn: StepFn
    order: int = 0
    when: Optional[HookPredicate] = None
    name: Optional[str] = None
    description: Optional[str] = None


# Forward-declare BaseModel for type checkers without importing pydantic at runtime
try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


@dataclass(frozen=True, slots=True)
class OpSpec:
    """
    The OpSpec is the single source of truth for an operation.

    Binder usage:
      • Builds request/response schemas (unless provided).
      • Chooses raw core (from core.crud) unless a custom `handler` is given.
      • Assembles HANDLER chain (pre/core/post/flushers) and per-phase hooks.
      • Registers REST & RPC if exposed. RBAC guard is applied per `rbac_guard_op`.
      • Auto-attaches START_TX/END_TX defaults unless persist="skip".
    """

    # Identity & exposure
    alias: str  # rpc/method name; may influence REST path suffix when path_suffix set
    target: TargetOp  # canonical verb for semantics
    table: Optional[type] = None  # set during collection/binding
    expose_routes: bool = True
    expose_rpc: bool = True
    expose_method: bool = True  # publish api.core.Resource.<alias>()

    # HTTP surface / behavior
    arity: Arity = "collection"
    http_methods: Optional[Tuple[str, ...]] = None
    path_suffix: Optional[str] = None
    tags: Tuple[str, ...] = field(default_factory=tuple)

    # Persistence & results
    persist: PersistPolicy = "default"  # "skip" → no START_TX/END_TX, writes forbidden
    returns: ReturnForm = (
        "model"  # "model" → serialize via schema; "raw" → pass-through
    )

    # Schema overrides (otherwise builder generates them)
    request_model: Optional[Type[BaseModel]] = None
    response_model: Optional[Type[BaseModel]] = None

    # Raw handler override (for custom ops); if None, binder uses core from core.crud
    handler: Optional[StepFn] = None

    # Hook contributions for any phases (see PHASES)
    hooks: Tuple[OpHook, ...] = field(default_factory=tuple)

    # RBAC or scoping linkage (guards may resolve by name)
    rbac_guard_op: Optional[str] = None

    # Canonical core references (filled by binder for diagnostics/back-compat)
    core: Optional[StepFn] = None  # resolved canonical implementation (if any)
    core_raw: Optional[StepFn] = None  # same as `core`; kept to preserve old naming

    # Extra metadata for integrators
    extra: Mapping[str, Any] = field(default_factory=dict)


# ───────────────────────────────────────────────────────────────────────────────
# Canonical verb set (helpful for validators/UIs)
# ───────────────────────────────────────────────────────────────────────────────

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
    "ReturnForm",
    "VerbAliasPolicy",
    "HookPhase",
    "PHASES",
    "Ctx",
    "StepFn",
    "HookPredicate",
    "OpHook",
    "OpSpec",
    "CANON",
]
