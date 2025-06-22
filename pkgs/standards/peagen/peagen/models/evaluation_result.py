from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import TIMESTAMP, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .task_run import Base


class EvaluationResult(Base):
    """Normalized evaluator output."""

    __tablename__ = "evaluation_results"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_runs.id"), primary_key=True
    )
    evaluator_name: Mapped[str] = mapped_column(String, primary_key=True)
    metric: Mapped[str] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.utcnow
    )
