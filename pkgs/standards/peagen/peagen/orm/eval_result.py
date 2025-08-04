from __future__ import annotations

from autoapi.v2.types import Column, String, JSON, PgUUID, ForeignKey, relationship
from autoapi.v2.tables import Base
from autoapi.v2.mixins import GUIDPk, Timestamped, Ownable

from .users import User


class EvalResult(Base, GUIDPk, Timestamped, Ownable):
    __tablename__ = "eval_results"
    work_id = Column(PgUUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"))
    label = Column(String)
    metrics = Column(JSON, nullable=False)
    owner = relationship(User, lazy="selectin")
    work = relationship("Work", back_populates="eval_results", lazy="selectin")
    analyses = relationship(
        "AnalysisResult",
        back_populates="eval_result",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


__all__ = ["EvalResult"]
