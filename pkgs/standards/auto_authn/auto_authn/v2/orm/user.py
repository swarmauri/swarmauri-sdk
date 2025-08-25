"""User model for the authentication service."""

from __future__ import annotations

import uuid

from autoapi.v2.tables import User as UserBase
from autoapi.v2.types import Column, LargeBinary, String, relationship


class User(UserBase):
    """Human principal with authentication credentials."""

    __table_args__ = ({"extend_existing": True, "schema": "authn"},)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(LargeBinary(60))
    api_keys = relationship(
        "auto_authn.v2.orm.tables.ApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )

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
