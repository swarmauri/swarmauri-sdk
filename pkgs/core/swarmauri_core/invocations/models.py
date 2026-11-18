"""Typed invocation envelopes; authority remains outside model arguments."""

from dataclasses import dataclass, field
from typing import Any

from swarmauri_core.permissions import Permission


@dataclass(frozen=True)
class InvocationContext:
    """Carry host-established identity and task authority."""

    actor: str
    task_id: str
    grant_id: str | None = None
    execution_id: str | None = None


@dataclass(frozen=True)
class EdgeAuthorizationBinding:
    """Configure an edge's caller, target and permission ceiling."""

    edge_id: str
    caller: str
    service: str
    operation: str
    permissions: tuple[Permission, ...]
    delegated: bool = True


@dataclass(frozen=True)
class InvocationRequest:
    """Describe one attempt; invocation_id is the idempotency key."""

    invocation_id: str
    edge_id: str
    task_id: str
    operation: str
    permission: Permission
    arguments: dict[str, Any] = field(default_factory=dict)
    parent_execution_id: str | None = None


@dataclass(frozen=True)
class InvocationResult:
    """Return a result correlated with the submitted invocation."""

    invocation_id: str
    value: Any
