from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Literal, Optional, Sequence, Type

PersistPolicy = Literal["default", "skip", "override"]
Arity = Literal["collection", "member"]
TargetOp = Literal[
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
    "clear",
    "custom",
]
ReturnForm = Literal["model", "raw"]  # raw later → optional

HookFn = Callable[..., Awaitable[None]]  # (table, ctx, db, request, payload) -> None


@dataclass(frozen=True)
class OpHook:
    phase: Any  # use autoapi.v2.hooks.Phase at call site
    fn: HookFn
    order: int = 0
    when: Optional[Callable[[dict], bool]] = None


@dataclass(frozen=True)
class OpSpec:
    alias: str
    target: TargetOp
    table: Type

    # facets
    expose_routes: bool = True
    expose_rpc: bool = True
    expose_method: bool = True

    # semantics
    arity: Optional[Arity] = None
    persist: PersistPolicy = "default"
    returns: ReturnForm = "model"

    # bindings
    handler: Optional[Callable[..., Any]] = None  # for override/custom

    # schemas & HTTP
    request_model: Optional[Type] = None
    response_model: Optional[Type] = None
    http_methods: Optional[Sequence[str]] = None
    path_suffix: Optional[str] = None
    tags: Optional[Sequence[str]] = None

    # RBAC
    rbac_guard_op: Optional[TargetOp] = None

    # per-verb hooks
    hooks: Sequence[OpHook] = ()

    # core persistence functions
    core: Optional[Callable[..., Any]] = None
    core_raw: Optional[Callable[..., Any]] = None
