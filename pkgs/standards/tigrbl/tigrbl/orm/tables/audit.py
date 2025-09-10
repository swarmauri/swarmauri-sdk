# tigrbl/tables/audit.py
import datetime as dt
from uuid import UUID

from . import Base
from ..mixins import GUIDPk, Timestamped
from ...specs import IO, F, acol, S
from ...types import DateTime, Integer, String, PgUUID, Mapped


class Change(Base, GUIDPk, Timestamped):
    __tablename__ = "changes"

    seq: Mapped[int] = acol(
        storage=S(Integer, primary_key=True),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )
    at: Mapped[dt.datetime] = acol(
        storage=S(DateTime, default=dt.datetime.utcnow),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )
    actor_id: Mapped[UUID | None] = acol(
        storage=S(PgUUID, nullable=True),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )
    table_name: Mapped[str] = acol(
        storage=S(String),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )
    row_id: Mapped[UUID | None] = acol(
        storage=S(PgUUID, nullable=True),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )
    action: Mapped[str] = acol(
        storage=S(String),
        field=F(),
        io=IO(out_verbs=("read", "list")),
    )


__all__ = ["Change"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
