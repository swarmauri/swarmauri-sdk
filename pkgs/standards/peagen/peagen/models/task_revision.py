"""Database tables for task revisions and DOE manifests."""
from __future__ import annotations

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from .task_run import Base


class Manifest(Base):
    """Unique DOE manifest fingerprint."""

    __tablename__ = "manifest"
    __table_args__ = (UniqueConstraint("design_hash", "plan_hash", name="uq_manifest_hashes"),)

    id = Column(Integer, primary_key=True)
    design_hash = Column(String, nullable=False)
    plan_hash = Column(String, nullable=False)


class TaskRevision(Base):
    """Append-only task revision history."""

    __tablename__ = "task_revision"

    id = Column(Integer, primary_key=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("task_runs.id", onupdate="RESTRICT", ondelete="RESTRICT"))
    parent_hash = Column(String, nullable=True)
    rev_hash = Column(String, nullable=False, unique=True)
    payload_hash = Column(String, nullable=False)
    payload_b64 = Column(String, nullable=False)
    ts_created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
