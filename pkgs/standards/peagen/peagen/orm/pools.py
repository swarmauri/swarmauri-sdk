from __future__ import annotations

from tigrbl.v3.orm.tables import Base
from tigrbl.v3.types import (
    JSON,
    String,
    UniqueConstraint,
    MutableDict,
    Mapped,
)
from tigrbl.v3.orm.mixins import GUIDPk, Bootstrappable, Timestamped, TenantBound
from tigrbl.v3.specs import S, acol
from tigrbl.v3 import hook_ctx
from peagen.defaults import DEFAULT_POOL_NAME, DEFAULT_POOL_ID, DEFAULT_TENANT_ID


class Pool(Base, GUIDPk, Bootstrappable, Timestamped, TenantBound):
    __tablename__ = "pools"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name"),
        {"schema": "peagen"},
    )
    name: Mapped[str] = acol(storage=S(String, nullable=False, unique=True))
    policy: Mapped[dict | None] = acol(
        storage=S(
            MutableDict.as_mutable(JSON),
            default=lambda: {"allowed_cidrs": ["0.0.0.0/0"], "max_instances": 100},
            nullable=True,
        )
    )
    DEFAULT_ROWS = [
        {
            "id": DEFAULT_POOL_ID,
            "name": DEFAULT_POOL_NAME,
            "tenant_id": DEFAULT_TENANT_ID,
        }
    ]

    @hook_ctx(ops="create", phase="POST_COMMIT")
    async def _post_create_register(cls, ctx):
        from peagen.gateway import log, queue

        log.info("entering post_pool_create")
        created = cls.schemas.read.out.model_validate(
            ctx["result"], from_attributes=True
        )
        await queue.sadd("pools", created.name)
        log.info("pool created: %s", created.name)
        ctx["result"] = created.model_dump()

        # hooks registered via @hook_ctx


__all__ = ["Pool"]
