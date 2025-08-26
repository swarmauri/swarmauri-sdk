"""Revoked token model."""

from __future__ import annotations

from autoapi.v3.tables import Base
from autoapi.v3.mixins import Timestamped
from autoapi.v3.specs import S, acol
from autoapi.v3.types import String
from autoapi.v3 import op_ctx


class RevokedToken(Base, Timestamped):
    __tablename__ = "revoked_tokens"
    __table_args__ = ({"schema": "authn"},)

    token: str = acol(storage=S(String(512), primary_key=True))

    @op_ctx(alias="revoke", target="create", arity="collection")
    def revoke(cls, ctx):
        pass


__all__ = ["RevokedToken"]
