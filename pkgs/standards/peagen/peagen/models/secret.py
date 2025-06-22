from __future__ import annotations

import datetime as dt

import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from .task_run import Base


class Secret(Base):
    __tablename__ = "secrets"
    __table_args__ = {"extend_existing": True}

    tenant_id = Column(String, primary_key=True)
    owner_fpr = Column(String, nullable=False)
    name = Column(String, primary_key=True)
    cipher = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=dt.datetime.utcnow)


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=dt.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
    )


class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=dt.datetime.utcnow)
