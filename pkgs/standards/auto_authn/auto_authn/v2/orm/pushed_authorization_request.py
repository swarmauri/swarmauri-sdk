"""Pushed authorization request model."""

from __future__ import annotations

import datetime as dt

from autoapi.v3.tables import Base
from autoapi.v3.mixins import Timestamped
from autoapi.v3.specs import S, acol
from autoapi.v3.types import JSON, String, TZDateTime
from autoapi.v3 import op_ctx


class PushedAuthorizationRequest(Base, Timestamped):
    __tablename__ = "par_requests"
    __table_args__ = ({"schema": "authn"},)

    request_uri: str = acol(storage=S(String(255), primary_key=True))
    params: dict = acol(storage=S(JSON, nullable=False))
    expires_at: dt.datetime = acol(storage=S(TZDateTime, nullable=False))

    @op_ctx(alias="par", target="create", arity="collection")
    def par(cls, ctx):
        pass


__all__ = ["PushedAuthorizationRequest"]
