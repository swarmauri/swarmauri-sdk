from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .task_run import Base


class AbuseRecord(Base):
    """Database model tracking abusive clients by IP address."""

    __tablename__ = "abuse_records"

    ip: Mapped[str] = mapped_column(String, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_seen: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.utcnow
    )
    banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
