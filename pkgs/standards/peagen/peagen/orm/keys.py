from __future__ import annotations

import uuid

from autoapi.v3.types import (
    Boolean,
    Column,
    String,
    UniqueConstraint,
    HookProvider,
    relationship,
)
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped, UserMixin
from peagen.orm.mixins import RepositoryRefMixin


class PublicKey(Base, GUIDPk, UserMixin, Timestamped):
    __tablename__ = "public_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "public_key"),
        {"schema": "peagen"},
    )
    title = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    read_only = Column(Boolean, default=True)


class GPGKey(Base, GUIDPk, UserMixin, Timestamped):
    __tablename__ = "gpg_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "gpg_key"),
        {"schema": "peagen"},
    )
    gpg_key = Column(String, nullable=False)


class DeployKey(Base, GUIDPk, RepositoryRefMixin, Timestamped, HookProvider):
    __tablename__ = "deploy_keys"
    __table_args__ = (
        UniqueConstraint("repository_id", "public_key"),
        {"schema": "peagen"},
    )
    title = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    read_only = Column(Boolean, default=True)

    repository = relationship("Repository", back_populates="deploy_keys")

    @classmethod
    async def _pre_create(cls, ctx):
        from peagen.gateway import log
        from pgpy import PGPKey

        log.info("entering pre_key_upload")
        params = ctx["env"].params
        pgp = PGPKey()
        pgp.parse(params.public_key)
        ctx["key_data"] = {
            "id": str(uuid.uuid4()),
            "user_id": None,
            "name": f"{pgp.fingerprint[:16]}-key",
            "public_key": params.public_key,
            "secret_id": None,
            "read_only": True,
        }
        ctx["fingerprint"] = pgp.fingerprint

    @classmethod
    async def _post_create(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_key_upload")
        params = ctx["env"].params
        log.info("key persisted (fingerprint=%s)", params.fingerprint)

    @classmethod
    async def _post_read(cls, ctx):
        from peagen.gateway import log

        log.info("entering POST_HANDLER")

    @classmethod
    async def _pre_delete(cls, ctx):
        from peagen.gateway import log

        log.info("entering pre_key_delete")
        params = ctx["env"].params
        ctx["fingerprint"] = params.fingerprint

    @classmethod
    async def _post_delete(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_key_delete")
        fp = ctx.get("fingerprint")
        log.info("key removed: %s", fp)

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v3 import _schema

        cls._SCreate = _schema(cls, verb="create")
        cls._SRead = _schema(cls, verb="read")
        cls._SDelete = _schema(cls, verb="delete")
        api.register_hook("PRE_TX_BEGIN", model="DeployKey", op="create")(
            cls._pre_create
        )
        api.register_hook("PRE_TX_BEGIN", model="DeployKey", op="delete")(
            cls._pre_delete
        )
        api.register_hook("POST_COMMIT", model="DeployKey", op="create")(
            cls._post_create
        )
        api.register_hook("POST_COMMIT", model="DeployKey", op="delete")(
            cls._post_delete
        )
        api.register_hook("POST_HANDLER", model="DeployKey", op="read")(cls._post_read)


__all__ = ["PublicKey", "GPGKey", "DeployKey"]
