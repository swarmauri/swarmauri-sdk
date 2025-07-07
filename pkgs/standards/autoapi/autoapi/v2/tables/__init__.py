# autoapi/tables/__init__.py
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = sa.MetaData(schema=None) 
