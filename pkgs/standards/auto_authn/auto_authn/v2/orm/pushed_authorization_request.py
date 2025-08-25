"""Pushed authorization request model."""

from __future__ import annotations

from autoapi.v2 import Base
from autoapi.v2.mixins import Timestamped
from autoapi.v2.types import Column, JSON, String, TZDateTime


class PushedAuthorizationRequest(Base, Timestamped):
    __tablename__ = "par_requests"
    __table_args__ = ({"schema": "authn"},)

    request_uri = Column(String(255), primary_key=True)
    params = Column(JSON, nullable=False)
    expires_at = Column(TZDateTime, nullable=False)


__all__ = ["PushedAuthorizationRequest"]
