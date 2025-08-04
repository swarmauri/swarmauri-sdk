from __future__ import annotations

from autoapi.v2.types import Column, Text, JSON, PgUUID, ForeignKey, relationship
from autoapi.v2.tables import Base
from autoapi.v2.mixins import GUIDPk, Timestamped, Ownable

from .users import User


class AnalysisResult(Base, GUIDPk, Timestamped, Ownable):
    __tablename__ = "analysis_results"
    eval_result_id = Column(
        PgUUID(as_uuid=True), ForeignKey("eval_results.id", ondelete="CASCADE")
    )
    summary = Column(Text)
    data = Column(JSON, default=dict, nullable=False)
    owner = relationship(User, lazy="selectin")
    eval_result = relationship("EvalResult", back_populates="analyses", lazy="selectin")


__all__ = ["AnalysisResult"]
