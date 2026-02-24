"""Shared external-reference helpers for Stripe-linked tables."""

from __future__ import annotations

from tigrbl.orm.mixins.fields import ExtRef
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import Mapped, String, declared_attr


class StripeExtRef(ExtRef):
    """ExtRef variant that defaults the provider column to ``"stripe"``."""

    provider_default: str = "stripe"
    provider_length: int | None = 32
    provider_nullable: bool = False
    provider_in_verbs: tuple[str, ...] = ()
    provider_out_verbs: tuple[str, ...] = ("read", "list")
    provider_mutable_verbs: tuple[str, ...] = ()

    @classmethod
    def _provider_constraints(cls) -> dict[str, int]:
        if cls.provider_length is None:
            return {}
        return {"max_length": cls.provider_length}

    @classmethod
    def _provider_type(cls):
        if cls.provider_length is None:
            return String
        return String(cls.provider_length)

    @declared_attr
    def provider(cls) -> Mapped[str]:
        return acol(
            spec=ColumnSpec(
                storage=S(
                    type_=cls._provider_type(),
                    nullable=cls.provider_nullable,
                    default=cls.provider_default,
                ),
                field=F(py_type=str, constraints=cls._provider_constraints()),
                io=IO(
                    in_verbs=cls.provider_in_verbs,
                    out_verbs=cls.provider_out_verbs,
                    mutable_verbs=cls.provider_mutable_verbs,
                ),
            )
        )


__all__ = ["StripeExtRef"]
