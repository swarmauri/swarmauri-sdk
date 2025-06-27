from __future__ import annotations

import datetime as dt
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AbuseRecordModel(Base):
    """Track abuse metrics for a given IP address."""

    __tablename__ = "abuse_records"

    ip: Mapped[str] = mapped_column(String, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_seen: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=dt.datetime.utcnow
    )
    banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AbuseRecord ip={self.ip!r} count={self.count} banned={self.banned}>"


AbuseRecord = AbuseRecordModel
