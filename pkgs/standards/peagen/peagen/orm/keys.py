from __future__ import annotations

import uuid

from autoapi.v3.orm.tables import Base
from autoapi.v3.types import (
    Boolean,
    String,
    UniqueConstraint,
    Mapped,
    relationship,
)
from autoapi.v3.orm.mixins import GUIDPk, Timestamped, UserColumn
from autoapi.v3.specs import S, acol
from autoapi.v3 import hook_ctx
from typing import TYPE_CHECKING
from peagen.orm.mixins import RepositoryRefMixin

if TYPE_CHECKING:  # pragma: no cover
    from .repositories import Repository


class PublicKey(Base, GUIDPk, UserColumn, Timestamped):
    __tablename__ = "public_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "public_key"),
        {"schema": "peagen"},
    )
    title: Mapped[str] = acol(storage=S(String, nullable=False))
    public_key: Mapped[str] = acol(storage=S(String, nullable=False))
    private_key: Mapped[str | None] = acol(storage=S(String, nullable=True))
    read_only: Mapped[bool] = acol(storage=S(Boolean, default=True))

    @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
    async def _pre_create(cls, ctx):
        from peagen.gateway.kms import wrap_key_with_kms

        params = ctx["env"].params
        priv = getattr(params, "private_key", None)
        if priv:
            params.private_key = await wrap_key_with_kms(priv)

    @hook_ctx(ops="read", phase="POST_HANDLER")
    async def _post_read(cls, ctx):
        from peagen.gateway.kms import unwrap_key_with_kms

        result = ctx.get("result")
        if isinstance(result, dict):
            priv = result.get("private_key")
            if priv:
                result["private_key"] = await unwrap_key_with_kms(priv)
        elif result is not None:
            priv = getattr(result, "private_key", None)
            if priv:
                result.private_key = await unwrap_key_with_kms(priv)

        # hooks registered via @hook_ctx


class GPGKey(Base, GUIDPk, UserColumn, Timestamped):
    __tablename__ = "gpg_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "gpg_key"),
        {"schema": "peagen"},
    )
    gpg_key: Mapped[str] = acol(storage=S(String, nullable=False))
    private_key: Mapped[str | None] = acol(storage=S(String, nullable=True))

    @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
    async def _pre_create(cls, ctx):
        from peagen.gateway.kms import wrap_key_with_kms

        params = ctx["env"].params
        priv = getattr(params, "private_key", None)
        if priv:
            params.private_key = await wrap_key_with_kms(priv)

    @hook_ctx(ops="read", phase="POST_HANDLER")
    async def _post_read(cls, ctx):
        from peagen.gateway.kms import unwrap_key_with_kms

        result = ctx.get("result")
        if isinstance(result, dict):
            priv = result.get("private_key")
            if priv:
                result["private_key"] = await unwrap_key_with_kms(priv)
        elif result is not None:
            priv = getattr(result, "private_key", None)
            if priv:
                result.private_key = await unwrap_key_with_kms(priv)

        # hooks registered via @hook_ctx


class DeployKey(Base, GUIDPk, RepositoryRefMixin, Timestamped):
    __tablename__ = "deploy_keys"
    __table_args__ = (
        UniqueConstraint("repository_id", "public_key"),
        {"schema": "peagen"},
    )
    title: Mapped[str] = acol(storage=S(String, nullable=False))
    public_key: Mapped[str] = acol(storage=S(String, nullable=False))
    private_key: Mapped[str | None] = acol(storage=S(String, nullable=True))
    read_only: Mapped[bool] = acol(storage=S(Boolean, default=True))

    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="deploy_keys"
    )

    @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
    async def _pre_create(cls, ctx):
        from peagen.gateway import log
        from peagen.gateway.kms import wrap_key_with_kms
        from pgpy import PGPKey

        log.info("entering pre_key_upload")
        params = ctx["env"].params
        pgp = PGPKey()
        pgp.parse(params.public_key)
        priv = getattr(params, "private_key", None)
        if priv:
            params.private_key = await wrap_key_with_kms(priv)
        ctx["key_data"] = {
            "id": str(uuid.uuid4()),
            "user_id": None,
            "name": f"{pgp.fingerprint[:16]}-key",
            "public_key": params.public_key,
            "private_key": getattr(params, "private_key", None),
            "secret_id": None,
            "read_only": True,
        }
        ctx["fingerprint"] = pgp.fingerprint

    @hook_ctx(ops="create", phase="POST_COMMIT")
    async def _post_create(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_key_upload")
        params = ctx["env"].params
        log.info("key persisted (fingerprint=%s)", params.fingerprint)

    @hook_ctx(ops="read", phase="POST_HANDLER")
    async def _post_read(cls, ctx):
        from peagen.gateway import log
        from peagen.gateway.kms import unwrap_key_with_kms

        log.info("entering POST_HANDLER")
        result = ctx.get("result")
        if isinstance(result, dict):
            priv = result.get("private_key")
            if priv:
                result["private_key"] = await unwrap_key_with_kms(priv)
        elif result is not None:
            priv = getattr(result, "private_key", None)
            if priv:
                result.private_key = await unwrap_key_with_kms(priv)

    @hook_ctx(ops="delete", phase="PRE_TX_BEGIN")
    async def _pre_delete(cls, ctx):
        from peagen.gateway import log

        log.info("entering pre_key_delete")
        params = ctx["env"].params
        ctx["fingerprint"] = params.fingerprint

    @hook_ctx(ops="delete", phase="POST_COMMIT")
    async def _post_delete(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_key_delete")
        fp = ctx.get("fingerprint")
        log.info("key removed: %s", fp)

        # hooks registered via @hook_ctx


__all__ = ["PublicKey", "GPGKey", "DeployKey"]
