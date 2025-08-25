# autoapi/tables/audit.py
import datetime as dt
from uuid import UUID

from . import Base
from ..mixins import GUIDPk, Timestamped
from ..specs import acol, IO, S
from ..types import DateTime, Integer, String, PgUUID


class Change(Base, GUIDPk, Timestamped):
    __tablename__ = "changes"

    seq: int = acol(
        storage=S(Integer, primary_key=True),
        io=IO(out_verbs=("read", "list")),
    )
    at: dt.datetime = acol(
        storage=S(DateTime, default=dt.datetime.utcnow),
        io=IO(out_verbs=("read", "list")),
    )
    actor_id: UUID | None = acol(
        storage=S(PgUUID, nullable=True),
        io=IO(out_verbs=("read", "list")),
    )
    table_name: str = acol(
        storage=S(String),
        io=IO(out_verbs=("read", "list")),
    )
    row_id: UUID | None = acol(
        storage=S(PgUUID, nullable=True),
        io=IO(out_verbs=("read", "list")),
    )
    action: str = acol(
        storage=S(String),
        io=IO(out_verbs=("read", "list")),
    )


__all__ = ["Change"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
