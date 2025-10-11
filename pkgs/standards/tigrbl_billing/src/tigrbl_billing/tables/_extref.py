"""Helpers for configuring Stripe external identifiers."""

from __future__ import annotations

# Stripe-specific helpers for configuring external identifiers.

from tigrbl.orm.mixins import ExtRef
from tigrbl.specs import ColumnSpec, F, IO, S
from tigrbl.types import String


class StripeExtRef(ExtRef):
    """ExtRef mixin preconfigured for Stripe-backed resources."""

    __extref_provider_spec__ = ColumnSpec(
        storage=S(type_=String(16), nullable=False, default="stripe"),
        field=F(py_type=str, constraints={"max_length": 16}),
        io=IO(out_verbs=("read", "list")),
    )


def stripe_external_id_spec(
    *,
    length: int = 64,
    unique: bool = True,
    index: bool = True,
    nullable: bool = True,
    in_verbs: tuple[str, ...] = ("create",),
    out_verbs: tuple[str, ...] = ("read", "list"),
    mutable_verbs: tuple[str, ...] | None = None,
    filter_ops: tuple[str, ...] | None = None,
) -> ColumnSpec:
    """Build a :class:`ColumnSpec` for a Stripe external identifier."""

    return ColumnSpec(
        storage=S(
            type_=String(length),
            unique=unique,
            index=index,
            nullable=nullable,
        ),
        field=F(py_type=str, constraints={"max_length": length}),
        io=IO(
            in_verbs=in_verbs,
            out_verbs=out_verbs,
            mutable_verbs=mutable_verbs or (),
            filter_ops=filter_ops or (),
        ),
    )


__all__ = ["StripeExtRef", "stripe_external_id_spec"]
