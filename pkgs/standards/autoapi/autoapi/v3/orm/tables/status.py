"""
StatusEnum table
----------------
Canonical store of workflow / lifecycle states.

• The `Status` enum below should always be the **only** source of truth for
  allowed values.  Every place in the codebase ‒ mix-ins, business logic,
  RPC schemas, etc. ‒ should import it instead of hard-coding strings.
• Domain tables that need a status field should `ForeignKey` to
  `status_enums.code` **or** just declare a `Column(SAEnum(Status, …))`
  if the FK is unnecessary.

If you add/remove a state later, just edit the `Status` enum – the rest
keeps working.
"""

from __future__ import annotations

from enum import StrEnum

from ...specs import acol, F, IO, S
from ...types import Integer, Mapped, SAEnum, String

from ._base import Base
from ..mixins import Timestamped  # created_at / updated_at


# ────────────────────────────────────────────────────────────────────────
# 1. In-memory application enum  (single source of truth)
# ────────────────────────────────────────────────────────────────────────
class Status(StrEnum):
    # queued / dispatching
    QUEUED = "queued"
    WAITING = "waiting"
    INPUT_REQUIRED = "input_required"
    AUTH_REQUIRED = "auth_required"

    # approvals
    APPROVED = "approved"
    REJECTED = "rejected"

    # execution lifecycle
    DISPATCHED = "dispatched"
    RUNNING = "running"
    PAUSED = "paused"

    # final states
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

    # (legacy / generic)
    PENDING = "pending"  # optional catch-all
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"
    DELETED = "deleted"


# ────────────────────────────────────────────────────────────────────────
# 2. Persistent lookup table
# ────────────────────────────────────────────────────────────────────────
class StatusEnum(Base, Timestamped):
    """
    id       – surrogate PK (easy FK if needed elsewhere)
    code     – canonical string value from the Status enum
    label    – human-readable label (“Paused”, “Failed”, …)
    """

    __tablename__ = "status_enums"

    id: Mapped[int] = acol(
        storage=S(Integer, primary_key=True, autoincrement=True),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )
    code: Mapped[Status] = acol(
        storage=S(
            SAEnum(Status, name="status_code_enum"),
            nullable=False,
            unique=True,
        ),
        field=F(py_type=Status),
        io=IO(out_verbs=("read", "list")),
    )
    label: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<StatusEnum {self.code}>"


__all__ = ["Status", "StatusEnum"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
