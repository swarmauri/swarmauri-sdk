# peagen/orm/api_key.py
from __future__ import annotations


from ...specs import acol, IO, S, F
from ...types import LargeBinary, Mapped, String

from ._base import Base
from ..mixins import ActiveToggle, GUIDPk, Timestamped, TenantBound


class Client(Base, GUIDPk, Timestamped, TenantBound, ActiveToggle):
    __tablename__ = "clients"
    __abstract__ = True
    # ---------------------------------------------------------------- columns --
    client_secret_hash: Mapped[bytes] = acol(
        storage=S(LargeBinary(60), nullable=False),
        field=F(),
        io=IO(in_verbs=("create",)),
    )
    redirect_uris: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(constraints={"max_length": 1000}),
        io=IO(),
    )
