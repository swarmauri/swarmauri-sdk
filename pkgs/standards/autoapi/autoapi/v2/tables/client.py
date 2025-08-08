# peagen/orm/api_key.py
from __future__ import annotations


from ..types import Column, String, LargeBinary, UniqueConstraint

from ._base import Base
from ..mixins import ActiveToggle, GUIDPk, Timestamped, TenantBound


class Client(Base, GUIDPk, Timestamped, TenantBound, ActiveToggle):
    __tablename__ = "clients"
    __abstract__  = True
    # ---------------------------------------------------------------- columns --
    client_secret_hash = Column(LargeBinary(60), nullable=False)
    redirect_uris = Column(String(1000), nullable=False)
