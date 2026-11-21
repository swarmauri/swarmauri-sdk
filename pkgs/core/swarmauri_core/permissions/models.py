"""Transport-independent permissions and authorization decisions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    """Allow one exact action on one exact resource within a tenant."""

    action: str
    resource: str
    tenant: str

    def __post_init__(self):
        if not all(
            isinstance(value, str) and value
            for value in (self.action, self.resource, self.tenant)
        ):
            raise ValueError("Permission fields must be non-empty")


@dataclass(frozen=True)
class AuthorizationDecision:
    """Return a decision without silently granting missing permissions."""

    allowed: bool
    reason: str = ""
