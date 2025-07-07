from __future__ import annotations

import datetime as dt
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from autoapi.v2.tables import Base, User
from autoapi.v2.mixins import GUIDPk, Timestamped, Ownable

class AbuseRecord(Base, GUIDPk, Timestamped, Ownable):
    """
    Track abuse metrics for a given IP address.
    • id          – surrogate UUID PK (from GUIDPk)
    • created_at  – first_seen (from Timestamped)
    • updated_at  – maintained automatically (from Timestamped)
    • owner_id    – who owns this record (from Ownable)
    """
    __tablename__ = "abuse_records"

    ip     = Column(String, nullable=False, unique=True, index=True)
    count  = Column(Integer, nullable=False, default=0)
    banned = Column(Boolean, nullable=False, default=False)

    # relationships
    owner = relationship(User, lazy="selectin")
