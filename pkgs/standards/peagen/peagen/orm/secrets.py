from __future__ import annotations

from autoapi.v3.types import (
    Column,
    String,
    UniqueConstraint,
    CheckConstraint,
    HookProvider,
    relationship,
)
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, OrgMixin, Timestamped, UserMixin
from peagen.orm.mixins import RepositoryMixin


class _SecretCoreMixin:
    name = Column(String(128), nullable=False)
    data = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    __table_args__ = (
        CheckConstraint("length(name) > 0", name="chk_name_nonempty"),
        {"schema": "peagen"},
    )


class UserSecret(Base, GUIDPk, _SecretCoreMixin, UserMixin, Timestamped):
    __tablename__ = "user_secrets"
    __table_args__ = (
        UniqueConstraint("user_id", "name"),
        *_SecretCoreMixin.__table_args__,
    )


class OrgSecret(Base, GUIDPk, _SecretCoreMixin, OrgMixin, Timestamped):
    __tablename__ = "org_secrets"
    __table_args__ = (
        UniqueConstraint("org_id", "name"),
        *_SecretCoreMixin.__table_args__,
    )


class RepoSecret(
    Base, GUIDPk, _SecretCoreMixin, RepositoryMixin, Timestamped, HookProvider
):
    __tablename__ = "repo_secrets"
    repository = relationship("Repository", back_populates="secrets")
    __table_args__ = (
        UniqueConstraint("repository_id", "name"),
        *_SecretCoreMixin.__table_args__,
    )

    @classmethod
    async def _post_create(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_secret_add")
        params = ctx["env"].params
        log.info("Secret stored successfully: %s", params.name)
        ctx["result"] = {"ok": True}

    @classmethod
    async def _post_delete(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_secret_delete")
        params = ctx["env"].params
        log.info("Secret deleted: %s", params.name)

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v3 import _schema

        cls._SRead = _schema(cls, verb="read")
        api.register_hook("POST_COMMIT", model="RepoSecret", op="create")(
            cls._post_create
        )
        api.register_hook("POST_COMMIT", model="RepoSecret", op="delete")(
            cls._post_delete
        )


__all__ = ["UserSecret", "OrgSecret", "RepoSecret"]
