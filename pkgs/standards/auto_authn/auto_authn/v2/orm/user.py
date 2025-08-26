"""User model for the authentication service."""

from __future__ import annotations

import uuid

from autoapi.v3.tables import User as UserBase
from autoapi.v3 import op_ctx, hook_ctx
from autoapi.v3.types import LargeBinary, String, relationship
from autoapi.v3.specs import IO, S, acol, vcol
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .api_key import ApiKey


class User(UserBase):
    """Human principal with authentication credentials."""

    __table_args__ = ({"extend_existing": True, "schema": "authn"},)
    email: str = acol(storage=S(String(120), nullable=False, unique=True))
    password_hash: bytes | None = acol(storage=S(LargeBinary(60)))
    _api_keys = relationship(
        "auto_authn.v2.orm.tables.ApiKey",
        back_populates="_user",
        cascade="all, delete-orphan",
    )
    api_keys: list["ApiKey"] = vcol(
        read_producer=lambda obj, _ctx: obj._api_keys,
        io=IO(out_verbs=("read", "list")),
    )

    @hook_ctx(ops=("create", "update"), phase="PRE_HANDLER")
    async def _hash_password(cls, ctx):
        payload = ctx.get("payload") or {}
        plain = payload.pop("password", None)
        if plain:
            from ..crypto import hash_pw

            payload["password_hash"] = hash_pw(plain)

    @op_ctx(alias="register", target="create", arity="collection")
    def register(cls, ctx):
        pass

    @classmethod
    def new(cls, tenant_id: uuid.UUID, username: str, email: str, password: str):
        return cls(
            tenant_id=tenant_id,
            username=username,
            email=email,
        )

    def verify_password(self, plain: str) -> bool:
        from ..crypto import verify_pw

        return verify_pw(plain, self.password_hash)


__all__ = ["User"]
