"""Revoked token model."""

from __future__ import annotations

from autoapi.v2 import Base
from autoapi.v2.mixins import Timestamped
from autoapi.v2.types import Column, String


class RevokedToken(Base, Timestamped):
    __tablename__ = "revoked_tokens"
    __table_args__ = ({"schema": "authn"},)

    token = Column(String(512), primary_key=True)


__all__ = ["RevokedToken"]
