"""
peagen.models.result.eval_result
================================

Quantitative evaluation output for a completed TaskRun.

Highlights
----------
• One-to-Many: TaskRun ➜ EvalResult (multiple metric sets per run).
• Stores a free-form `metrics` JSON blob plus an optional `label`.
• Bidirectional link to AnalysisResult rows for deeper post-hoc insights.
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class EvalResult(BaseModel):
    """
    Numeric or structured evaluation results for a TaskRun.
    """

    __tablename__ = "eval_results"

    # ───────────────────── Columns ─────────────────────
    task_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_runs.id", ondelete="CASCADE"),
        nullable=False,
    )

    label: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        doc="Optional label, e.g. 'validation-set', 'test-set-A'.",
    )

    metrics: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        doc="Free-form metrics dict (accuracy, F1, BLEU …).",
    )

    # ───────────────── Relationships ───────────────────
    task_run: Mapped["TaskRun"] = relationship(
        "TaskRun",
        back_populates="eval_results",
        lazy="selectin",
    )

    analyses: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="eval_result",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<EvalResult id={self.id} task_run={self.task_run_id} "
            f"label={self.label or '∅'}>"
        )
