from __future__ import annotations

from autoapi.v3.orm.tables import Base
from autoapi.v3.types import JSON, PgUUID, String, Mapped, relationship
from autoapi.v3.orm.mixins import GUIDPk, Timestamped, Ownable, TenantBound
from autoapi.v3.specs import S, acol
from autoapi.v3.column.storage_spec import ForeignKeySpec
from typing import TYPE_CHECKING

from .users import User

if TYPE_CHECKING:  # pragma: no cover
    from .works import Work
    from .analysis_result import AnalysisResult


class EvalResult(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "eval_results"
    __table_args__ = ({"schema": "peagen"},)
    work_id: Mapped[PgUUID | None] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec("peagen.works.id", on_delete="CASCADE"),
        )
    )
    label: Mapped[str | None] = acol(storage=S(String))
    metrics: Mapped[dict] = acol(storage=S(JSON, nullable=False))
    owner: Mapped[User] = relationship(User, lazy="selectin")
    work: Mapped["Work | None"] = relationship(
        "Work", back_populates="eval_results", lazy="selectin"
    )
    analyses: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="eval_result",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


__all__ = ["EvalResult"]
