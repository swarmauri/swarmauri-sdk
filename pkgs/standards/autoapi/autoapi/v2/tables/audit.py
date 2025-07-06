# autoapi/tables/audit.py
import datetime as dt
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from . import Base
from ..mixins import GUIDPk, Timestamped

class Change(Base, GUIDPk, Timestamped):
    __tablename__ = "changes"
    seq        = Column(Integer, primary_key=True)
    at         = Column(DateTime, default=dt.datetime.utcnow)
    actor_id   = Column(UUID)
    table_name = Column(String)
    row_id     = Column(UUID)
    action     = Column(String)
