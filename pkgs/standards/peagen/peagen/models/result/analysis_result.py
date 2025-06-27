"""
peagen.models.result.analysis_result
====================================

Post-hoc analysis attached to an EvalResult.

Typical use-cases
-----------------
• Error analysis summaries
• Confusion matrices
• Saliency / attention heat-maps
• Human evaluation notes

Data Model
----------
EvalResult 1 ─⟶ 0..n AnalysisResult
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from .eval_result import EvalResultModel

from ..base import BaseModel


class AnalysisResultModel(BaseModel):
    """
    Qualitative or extended quantitative analysis of an EvalResult.
    """

    __tablename__ = "analysis_results"

    # ───────────────────── Columns ─────────────────────
    eval_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_results.id", ondelete="CASCADE"),
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional short text summary of findings.",
    )

    data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Structured analysis payload (confusion matrix, charts, etc.).",
    )

    # ───────────────── Relationships ───────────────────
    eval_result: Mapped["EvalResultModel"] = relationship(
        "EvalResultModel",
        back_populates="analyses",
        lazy="selectin",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<AnalysisResult id={self.id} eval={self.eval_result_id}>"


AnalysisResult = AnalysisResultModel
