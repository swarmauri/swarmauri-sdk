"""Product table (Stripe product mirror + local metadata)."""

from __future__ import annotations

from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped, ActiveToggle
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import String, Text, JSONB, Mapped

from ._extref import StripeExtRef, stripe_external_id_spec


class Product(Base, GUIDPk, Timestamped, ActiveToggle, StripeExtRef):
    __tablename__ = "billing_products"

    stripe_product_id: Mapped[str]
    __extref_external_id_attr__ = "stripe_product_id"
    __extref_external_id_column__ = "stripe_product_id"
    __extref_external_id_spec__ = stripe_external_id_spec(
        nullable=False,
        in_verbs=("create",),
        out_verbs=("read", "list"),
        mutable_verbs=("update",),
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

    metadata_: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("update", "replace"),
        ),
        name="metadata",
    )


__all__ = ["Product"]
