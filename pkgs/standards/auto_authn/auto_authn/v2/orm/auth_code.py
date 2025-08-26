"""Authorization code model."""

from __future__ import annotations

import datetime as dt
import uuid

from autoapi.v3.tables import Base
from autoapi.v3.mixins import TenantMixin, Timestamped, UserMixin
from autoapi.v3.specs import S, acol
from autoapi.v3.specs.storage_spec import ForeignKeySpec
from autoapi.v3.types import JSON, PgUUID, String, TZDateTime
from autoapi.v3 import op_ctx


class AuthCode(Base, Timestamped, UserMixin, TenantMixin):
    __tablename__ = "auth_codes"
    __table_args__ = ({"schema": "authn"},)

    code: str = acol(storage=S(String(128), primary_key=True))
    client_id: uuid.UUID = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.clients.id"),
            nullable=False,
        )
    )
    redirect_uri: str = acol(storage=S(String(1000), nullable=False))
    code_challenge: str | None = acol(storage=S(String, nullable=True))
    nonce: str | None = acol(storage=S(String, nullable=True))
    scope: str | None = acol(storage=S(String, nullable=True))
    expires_at: dt.datetime = acol(storage=S(TZDateTime, nullable=False))
    claims: dict | None = acol(storage=S(JSON, nullable=True))

    @op_ctx(alias="exchange", target="delete", arity="member")
    def exchange(cls, ctx, obj):
        return obj


__all__ = ["AuthCode"]
