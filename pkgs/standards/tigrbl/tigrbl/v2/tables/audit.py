# tigrbl/tables/audit.py
import datetime as dt

from . import Base
from ..mixins import GUIDPk, Timestamped
from ..types import Column, DateTime, Integer, String, PgUUID


class Change(Base, GUIDPk, Timestamped):
    __tablename__ = "changes"
    seq = Column(Integer, primary_key=True)
    at = Column(DateTime, default=dt.datetime.utcnow)
    actor_id = Column(PgUUID)
    table_name = Column(String)
    row_id = Column(PgUUID)
    action = Column(String)


__all__ = ["Change"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
