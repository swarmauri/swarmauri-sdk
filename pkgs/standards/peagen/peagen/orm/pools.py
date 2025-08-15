from __future__ import annotations

from autoapi.v3.types import (
    JSON,
    Column,
    String,
    UniqueConstraint,
    MutableDict,
    HookProvider,
)
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Bootstrappable, Timestamped, TenantBound
from peagen.defaults import DEFAULT_POOL_NAME, DEFAULT_POOL_ID, DEFAULT_TENANT_ID


class Pool(Base, GUIDPk, Bootstrappable, Timestamped, TenantBound, HookProvider):
    __tablename__ = "pools"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name"),
        {"schema": "peagen"},
    )
    name = Column(String, nullable=False, unique=True)
    policy = Column(
        MutableDict.as_mutable(JSON),
        default=lambda: {"allowed_cidrs": ["0.0.0.0/0"], "max_instances": 100},
        nullable=True,
    )
    DEFAULT_ROWS = [
        {
            "id": DEFAULT_POOL_ID,
            "name": DEFAULT_POOL_NAME,
            "tenant_id": DEFAULT_TENANT_ID,
        }
    ]

    @classmethod
    async def _post_create_register(cls, ctx):
        from peagen.gateway import log, queue

        log.info("entering post_pool_create")
        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        await queue.sadd("pools", created.name)
        log.info("pool created: %s", created.name)
        ctx["result"] = created.model_dump()

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v3 import _schema

        cls._SRead = _schema(cls, verb="read")
        api.register_hook("POST_COMMIT", model="Pool", op="create")(
            cls._post_create_register
        )


__all__ = ["Pool"]
