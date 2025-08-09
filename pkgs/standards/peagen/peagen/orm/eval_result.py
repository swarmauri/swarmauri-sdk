from __future__ import annotations

from autoapi.v2.types import Column, String, JSON, PgUUID, ForeignKey, relationship
from autoapi.v2.tables import Base
from autoapi.v2.mixins import GUIDPk, Timestamped, Ownable, TenantBound

from .users import User


class EvalResult(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "eval_results"
    __table_args__= ({"schema": "peagen"},)
    work_id = Column(PgUUID(as_uuid=True), ForeignKey("peagen.works.id", ondelete="CASCADE"))
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
