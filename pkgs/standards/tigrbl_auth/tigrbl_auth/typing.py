"""
tigrbl_auth.typing
==================

Pure-typing utilities for the AuthN service.
No runtime dependencies outside stdlib.

Key exports
-----------
Principal     : `Protocol` describing the minimal fields required by
                downstream helpers (e.g., require_scope()).
StrUUID       : Type alias for canonical 36-char UUID strings.
JWTPayload    : TypedDict for decoded JWT claims used across the codebase.
"""

from __future__ import annotations

import uuid
from typing import Protocol, TypedDict, runtime_checkable, NewType

# ---------------------------------------------------------------------
# UUID helpers
# ---------------------------------------------------------------------
StrUUID = NewType("StrUUID", str)  # 36-char uuid string, runtime = str


def uuid_str() -> StrUUID:
    """Return a new random UUID *string* in canonical form."""
    return StrUUID(str(uuid.uuid4()))


# ---------------------------------------------------------------------
# JWT payload schema
# ---------------------------------------------------------------------
class JWTPayload(TypedDict, total=False):
    sub: StrUUID  # subject (user.id)
    tid: StrUUID  # tenant id
    typ: str  # "access" | "refresh"
    iat: int  # issued-at (posix seconds)
    exp: int  # expiry (posix seconds)
    jti: str  # token id


# ---------------------------------------------------------------------
# Principal protocol  (shared by authz clients & FastAPI deps)
# ---------------------------------------------------------------------
@runtime_checkable
class Principal(Protocol):
    """
    Minimum surface needed by downstream code.

    Any object (DTO, ORM instance, dict) satisfying this Protocol
    can be passed into auth helpers such as `require_scope`.
    """

    id: StrUUID  # primary key of the user
    tenant_id: StrUUID  # partition identifier
