"""Customer↔ConnectedAccount mapping."""
from __future__ import annotations

from enum import Enum

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import Mapped, String, JSONB, UniqueConstraint, PgUUID, UUID, SAEnum

class AccountRole(Enum):
    PAYER = "payer"
    PAYEE = "payee"
    BOTH = "both"

class CustomerAccountLink(Base, GUIDPk, Timestamped):
    __tablename__ = "customer_account_links"

    customer_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="customers.id"),
                nullable=False,
                index=True),
            field=F(py_type=UUID),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    connected_account_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="connected_accounts.id"),
                nullable=False,
                index=True),
            field=F(py_type=UUID),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    role: Mapped[AccountRole] = acol(
        spec=ColumnSpec(
            storage=S(type_=SAEnum, nullable=False),
            field=F(py_type=AccountRole),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    metadata: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict, nullable=False),
            field=F(py_type=dict),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    __table_args__ = (
        UniqueConstraint("customer_id", "connected_account_id", name="uq_cal_customer_connected"))

__all__ = ["CustomerAccountLink", "AccountRole"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]

def __dir__():
    return sorted(__all__)
