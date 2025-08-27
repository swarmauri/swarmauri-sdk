from __future__ import annotations

from autoapi.v3.tables import Base
from autoapi.v3.types import (
    String,
    UniqueConstraint,
    CheckConstraint,
    HookProvider,
    relationship,
    Mapped,
)
from autoapi.v3.mixins import GUIDPk, OrgMixin, Timestamped, UserMixin
from autoapi.v3.specs import S, acol
from autoapi.v3 import hook_ctx
from typing import TYPE_CHECKING
from peagen.orm.mixins import RepositoryMixin

if TYPE_CHECKING:  # pragma: no cover
    from .repositories import Repository


class _SecretCoreMixin:
    name: Mapped[str] = acol(storage=S(String(128), nullable=False))
    data: Mapped[str] = acol(storage=S(String, nullable=False))
    desc: Mapped[str | None] = acol(storage=S(String, nullable=True))
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
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="secrets"
    )
    __table_args__ = (
        UniqueConstraint("repository_id", "name"),
        *_SecretCoreMixin.__table_args__,
    )

    @hook_ctx(ops="create", phase="POST_COMMIT")
    async def _post_create(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_secret_add")
        params = ctx["env"].params
        log.info("Secret stored successfully: %s", params.name)
        ctx["result"] = {"ok": True}

    @hook_ctx(ops="delete", phase="POST_COMMIT")
    async def _post_delete(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_secret_delete")
        params = ctx["env"].params
        log.info("Secret deleted: %s", params.name)

        # hooks registered via @hook_ctx


__all__ = ["UserSecret", "OrgSecret", "RepoSecret"]
