from __future__ import annotations

from autoapi.v3.types import Column, Text, JSON, PgUUID, ForeignKey, relationship
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped, Ownable, TenantBound


from .users import User


class AnalysisResult(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "analysis_results"
    __table_args__ = ({"schema": "peagen"},)
    eval_result_id = Column(
        PgUUID(as_uuid=True), ForeignKey("peagen.eval_results.id", ondelete="CASCADE")
    )
    summary = Column(Text)
    data = Column(JSON, default=dict, nullable=False)
    owner = relationship(User, lazy="selectin")
    eval_result = relationship("EvalResult", back_populates="analyses", lazy="selectin")


__all__ = ["AnalysisResult"]
