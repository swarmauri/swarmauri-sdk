"""Product table (Stripe product mirror + local metadata)."""

from __future__ import annotations

from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped, ActiveToggle
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import String, Text, JSONB, Mapped


class Product(Base, GUIDPk, Timestamped, ActiveToggle):
    __tablename__ = "billing_products"

    # Stripe product id (e.g., "prod_...")
    stripe_product_id: Mapped[str] = acol(
        storage=S(type_=String(64), unique=True, index=True, nullable=False),
        field=F(py_type=str, constraints={"max_length": 64}),
        io=IO(
            in_verbs=("create"),
            out_verbs=("read", "list"),
            mutable_verbs=("update"),
        ),
    )

    name: Mapped[str] = acol(
        storage=S(type_=String(255), nullable=False, index=True),
        field=F(py_type=str, constraints={"max_length": 255}),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("update", "replace"),
        ),
    )

    description: Mapped[str | None] = acol(
        storage=S(type_=Text, nullable=True),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("update", "replace"),
        ),
    )

    metadata: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("update", "replace"),
        ),
    )


__all__ = ["Product"]
