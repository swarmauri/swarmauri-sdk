"""
StatusEnum table
----------------
Provides a single source of truth for workflow / lifecycle states.
Use the `Status` enum for type-safe references in your code and FK
to `status_enums.code` from domain tables that need a status field.
"""
from __future__ import annotations

from enum import StrEnum
from sqlalchemy import Column, String, Enum as SAEnum, Integer

from ._base     import Base
from ..mixins   import Timestamped                # created_at / updated_at

# --------------------------------------------------------------------- #
# 1. Application-level enumeration (type-safe, IDE-friendly)            #
# --------------------------------------------------------------------- #
class Status(StrEnum):
    PENDING   = "pending"
    ACTIVE    = "active"
    SUSPENDED = "suspended"
    DISABLED  = "disabled"
    DELETED   = "deleted"

# --------------------------------------------------------------------- #
# 2. Persistent table of allowed values                                 #
# --------------------------------------------------------------------- #
class StatusEnum(Base, Timestamped):
    """
    id        – surrogate PK for easy FK’ing if desired.
    code      – canonical string, unique.
    label     – human-readable name (“Suspended”, …).
    """
    __tablename__ = "status_enums"

    id    = Column(Integer, primary_key=True, autoincrement=True)
    code  = Column(SAEnum(Status, name="status_code_enum"), unique=True, nullable=False)
    label = Column(String, nullable=False)

    # Optional: nice __repr__
    def __repr__(self) -> str:                       # noqa: D401
        return f"<StatusEnum {self.code}>"
