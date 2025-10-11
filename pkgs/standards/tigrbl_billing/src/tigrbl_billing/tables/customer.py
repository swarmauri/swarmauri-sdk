"""Customer model – payer identity and Stripe linkage."""
from __future__ import annotations

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import Mapped, String, JSONB, Boolean, UniqueConstraint

class Customer(Base, GUIDPk, Timestamped):
    __tablename__ = "customers"


    stripe_customer_id: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True, unique=True, index=True),
            field=F(py_type=str | None),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    email: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True, index=True),
            field=F(py_type=str | None, constraints={"max_length": 320, "format": "email"}),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    name: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    default_payment_method_ref: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None, constraints={"examples": ["pm_123..."]}),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    tax_exempt: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None, constraints={"enum": ["none","exempt","reverse"]}),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    active: Mapped[bool] = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, default=True, nullable=False),
            field=F(py_type=bool),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    metadata: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict, nullable=False),
            field=F(py_type=dict),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    __table_args__ = (
        UniqueConstraint("stripe_customer_id", name="uq_customers_stripe_customer_id"))

__all__ = ["Customer"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]

def __dir__():
    return sorted(__all__)
