"""PriceTier table – per-price bands (graduated/volume)."""

from __future__ import annotations

from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import Integer, Mapped
from tigrbl.orm.mixins.utils import _infer_schema


class PriceTier(Base, GUIDPk, Timestamped):
    __tablename__ = "billing_price_tiers"

    price_id: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=str,
                fk=ForeignKeySpec(target=lambda cls: f"{_infer_schema(cls)}.billing_prices.id"),
                nullable=False,
                index=True),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read","list")))
    )

    up_to: Mapped[int | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=True, index=True),
            field=F(py_type=int),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read","list")))
    )

    flat_amount: Mapped[int | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=True),
            field=F(py_type=int),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read","list")))
    )

    unit_amount: Mapped[int | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=True, check="NOT (flat_amount IS NULL AND unit_amount IS NULL)"),
            field=F(py_type=int),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read","list")))
    )


__all__ = ["PriceTier"]
