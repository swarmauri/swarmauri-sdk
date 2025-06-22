from __future__ import annotations

import datetime as dt

from sqlalchemy import Column, String, TIMESTAMP

from .task_run import Base


class Secret(Base):
    __tablename__ = "secrets"

    tenant_id = Column(String, primary_key=True)
    owner_fpr = Column(String, nullable=False)
    name = Column(String, primary_key=True)
    cipher = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=dt.datetime.utcnow)
