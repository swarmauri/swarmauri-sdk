from __future__ import annotations

from autoapi.v2.types import Column, String, SAEnum
from autoapi.v2.tables import Base
from autoapi.v2.mixins import GUIDPk, Timestamped


class Key(Base, GUIDPk, Timestamped):
    __tablename__ = "Key"

    name = Column(String(120), nullable=False, index=True)
    algorithm = Column(SAEnum("AES256_GCM", name="KeyAlg"), nullable=False)
    status = Column(SAEnum("enabled", name="KeyStatus"), nullable=False)
    primary_version = Column(int, default=1, nullable=False)

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        # Hooks are registered in key_hooks.py via this callback if needed
        from ..hooks.key_hooks import register_key_hooks

        register_key_hooks(api)
