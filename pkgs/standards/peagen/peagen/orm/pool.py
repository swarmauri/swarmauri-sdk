from __future__ import annotations

from autoapi.v2 import AutoAPI, Phase
from autoapi.v2.mixins import (
    Bootstrappable,
    GUIDPk,
    HookProvider,
    TenantBound,
    Timestamped,
)
from autoapi.v2.tables import Base
from autoapi.v2.types import JSON, Column, MutableDict, String, UniqueConstraint
from peagen.defaults import DEFAULT_POOL_ID, DEFAULT_POOL_NAME, DEFAULT_TENANT_ID


class Pool(Base, GUIDPk, Bootstrappable, Timestamped, TenantBound, HookProvider):
    __tablename__ = "pools"
    __table_args__ = (UniqueConstraint("tenant_id", "name"),)
    name = Column(String, nullable=False, unique=True)
    policy = Column(
        MutableDict.as_mutable(JSON),
        default=lambda: {"allowed_cidrs": [], "max_instances": None},
        nullable=True,
    )

    DEFAULT_ROWS = [
        {
            "id": DEFAULT_POOL_ID,
            "name": DEFAULT_POOL_NAME,
            "tenant_id": DEFAULT_TENANT_ID,
            "policy": {"allowed_cidrs": [], "max_instances": None},
        }
    ]

    @classmethod
    async def _post_create_register(cls, ctx):
        from peagen.gateway import log, queue

        log.info("entering post_pool_create")
        name = ctx["env"].params.name
        await queue.sadd("pools", name)
        log.info("pool created: %s", name)
        ctx["result"] = cls._SRead(name=name).model_dump()

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        cls._SRead = AutoAPI.get_schema(cls, "read")
        api.register_hook(Phase.POST_COMMIT, model="Pool", op="create")(
            cls._post_create_register
        )
