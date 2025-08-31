# autoapi/v3/opspec/types.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping, Optional, Tuple, Type, Union

from ..hook.types import PHASE, HookPhase, PHASES, Ctx, StepFn, HookPredicate
from ..hook_spec import HookSpec as OpHook

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
# Engine binding (optional, used by resolver precedence: op > table > api > app)
# ───────────────────────────────────────────────────────────────────────────────

# DSN string (e.g., "sqlite+memory://", "sqlite:///path.db",
# "postgresql://user:pwd@host:5432/db", "postgresql+asyncpg://…")
# or a structured mapping as used elsewhere in v3 ({"kind":"sqlite"/"postgres", ...}).
DBSpec = Union[str, Mapping[str, Any]]


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
      - `db` allows per-op DB routing (string DSN or structured mapping).
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
    db: Optional[DBSpec] = None

    # HTTP behavior
    arity: Arity = "collection"
    http_methods: Optional[Tuple[str, ...]] = None
    path_suffix: Optional[str] = None
    tags: Tuple[str, ...] = field(default_factory=tuple)
    status_code: Optional[int] = None

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
CANON: Tuple[TargetOp, ...] = (
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
)

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
    "SchemaKind",
    "SchemaRef",
    "SchemaArg",
    "DBSpec",
    "OpHook",
    "OpSpec",
    "CANON",
]
