from __future__ import annotations

from tigrbl.orm.tables import Base
from tigrbl.types import JSON, PgUUID, Text, Mapped, relationship
from tigrbl.orm.mixins import GUIDPk, Timestamped, Ownable, TenantBound
from tigrbl.specs import S, acol
from tigrbl.column.storage_spec import ForeignKeySpec
from typing import TYPE_CHECKING

from .users import User

if TYPE_CHECKING:  # pragma: no cover
    from .eval_result import EvalResult


class AnalysisResult(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "analysis_results"
    __table_args__ = ({"schema": "peagen"},)
    eval_result_id: Mapped[PgUUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec("peagen.eval_results.id", on_delete="CASCADE"),
        )
    )
    summary: Mapped[str | None] = acol(storage=S(Text))
    data: Mapped[dict] = acol(storage=S(JSON, default=dict, nullable=False))
    owner: Mapped[User] = relationship(User, lazy="selectin")
    eval_result: Mapped["EvalResult"] = relationship(
        "EvalResult", back_populates="analyses", lazy="selectin"
    )


__all__ = ["AnalysisResult"]
