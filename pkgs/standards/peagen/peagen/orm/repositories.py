from __future__ import annotations

from autoapi.v2.tables import Base
from autoapi.v2.types import (
    Column,
    String,
    UniqueConstraint,
    relationship,
    HookProvider,
)
from autoapi.v2.mixins import GUIDPk, Timestamped, TenantBound, Ownable, StatusMixin


class Repository(
    Base, GUIDPk, Timestamped, TenantBound, Ownable, StatusMixin, HookProvider
):
    """
    A code or data repository that lives under a tenant.
    – parent of Secrets & DeployKeys
    """

    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("url"),
        UniqueConstraint("tenant_id", "name"),
    )
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    default_branch = Column(String, default="main")
    commit_sha = Column(String(length=40), nullable=True)
    remote_name = Column(String, nullable=False, default="origin")

    secrets = relationship(
        "RepoSecret", back_populates="repository", cascade="all, delete-orphan"
    )
    deploy_keys = relationship(
        "DeployKey", back_populates="repository", cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

    @classmethod
    async def _post_create(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_repository_create")
        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        log.info("repository created: %s (%s)", created.name, created.url)
        ctx["result"] = created.model_dump()

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import AutoAPI, Phase

        cls._SRead = AutoAPI.get_schema(cls, "read")
        api.register_hook(Phase.POST_COMMIT, model="Repository", op="create")(
            cls._post_create
        )


__all__ = ["Repository"]
