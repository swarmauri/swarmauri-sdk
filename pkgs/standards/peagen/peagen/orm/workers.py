from __future__ import annotations

from tigrbl.orm.tables import Base
from tigrbl.types import (
    JSON,
    PgUUID,
    UUID,
    String,
    MutableDict,
    relationship,
    AllowAnonProvider,
    Mapped,
)
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import IO, S, acol
from tigrbl.column.storage_spec import ForeignKeySpec
from tigrbl import hook_ctx
from peagen.defaults import DEFAULT_POOL_ID, WORKER_KEY, WORKER_TTL

from .pools import Pool


_RW_IO = {"in_verbs": ("create", "replace", "update"), "out_verbs": ("read", "list")}


class Worker(Base, GUIDPk, Timestamped, AllowAnonProvider):
    __tablename__ = "workers"
    __table_args__ = ({"schema": "peagen"},)

    __tigrbl_allow_anon__ = {"create"}  # allow unauthenticated worker registration

    pool_id: Mapped[PgUUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec("peagen.pools.id"),
            nullable=False,
            default=DEFAULT_POOL_ID,
        ),
        io=IO(**_RW_IO),
    )
    url: Mapped[str] = acol(
        storage=S(String, nullable=False),
        io=IO(**_RW_IO),
    )
    advertises: Mapped[dict | None] = acol(
        storage=S(
            MutableDict.as_mutable(JSON),
            default=lambda: {},
            nullable=True,
        ),
        io=IO(**_RW_IO),
    )
    handler_map: Mapped[dict | None] = acol(
        storage=S(
            MutableDict.as_mutable(JSON),
            default=lambda: {},
            nullable=True,
        ),
        io=IO(alias_in="handlers", alias_out="handlers", **_RW_IO),
    )

    pool: Mapped[Pool] = relationship(Pool, backref="workers")

    # ─── internal helpers -------------------------------------------------
    @staticmethod
    def _client_ip(request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.headers.get("x-real-ip") or request.client.host

    @staticmethod
    def _as_redis_hash(model) -> dict[str, str]:
        import json

        out: dict[str, str] = {}
        for k, v in model.model_dump(mode="json").items():
            if v is None:
                continue
            if isinstance(v, (dict, list)):
                out[k] = json.dumps(v, separators=(",", ":"))
            else:
                out[k] = str(v)
        return out

    @staticmethod
    def _check_pool_policy(policy, ip: str, count: int) -> None:
        import ipaddress
        from peagen.transport.jsonrpc import RPCException

        allowed = policy.get("allowed_cidrs") or []
        if allowed:
            addr = ipaddress.ip_address(ip)
            if not any(addr in ipaddress.ip_network(cidr) for cidr in allowed):
                raise RPCException(code=-32602, message="worker IP not allowed")

        max_instances = policy.get("max_instances")
        if max_instances is not None and count >= int(max_instances):
            raise RPCException(code=-32602, message="pool at capacity")

    # ─── Tigrbl hook callbacks ------------------------------------------
    @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
    async def _pre_create_policy_gate(cls, ctx):
        from peagen.gateway import log

        log.info("entering pre_worker_create_policy_gate")
        params = ctx["env"].params
        pool_id = params["pool_id"]
        if isinstance(pool_id, str):
            pool_id = UUID(pool_id)
        ip = cls._client_ip(ctx["request"])

        def _get_policy_and_count(session):
            pool = session.get(Pool, pool_id)
            count = session.query(cls).filter(cls.pool_id == pool_id).count()
            return (pool.policy if pool else {}, count)

        policy, count = await ctx["db"].run_sync(_get_policy_and_count)
        log.info(
            "loaded pool policy %s with %s existing workers for pool %s",
            policy,
            count,
            pool_id,
        )
        cls._check_pool_policy(policy or {}, ip, count)
        log.info("exiting pre_worker_create_policy_gate")

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    async def _post_create_cache_pool(cls, ctx):
        from peagen.gateway import log, queue

        log.info("entering post_worker_create_cache_pool")
        created = cls.schemas.read.out.model_validate(
            ctx["result"], from_attributes=True
        )
        log.info("worker %s joined pool_id %s", created.id, created.pool_id)
        try:
            await queue.sadd(f"pool_id:{created.pool_id}:members", str(created.id))
            log.info(
                "cached worker %s as member of pool %s",
                created.id,
                created.pool_id,
            )
        except Exception as exc:  # noqa: BLE001
            log.error("failure to add member to pool queue. err: %s", exc)
        log.info("exiting post_worker_create_cache_pool")

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    async def _post_create_cache_worker(cls, ctx):
        from peagen.gateway import log, queue

        log.info("entering post_worker_create_cache_worker")
        created = cls.schemas.read.out.model_validate(
            ctx["result"], from_attributes=True
        )
        try:
            key = WORKER_KEY.format(str(created.id))
            await queue.hset(key, cls._as_redis_hash(created))
            await queue.expire(key, WORKER_TTL)
            log.info("cached `%s`", key)
        except Exception as exc:  # noqa: BLE001
            log.error("failure to add worker. err: %s", exc)
        try:
            from peagen.gateway._publish import _publish_event

            await _publish_event(queue, "Worker.create", created)
            log.info("published Worker.create event for %s", created.id)
        except Exception as exc:  # noqa: BLE001
            log.error("failure to _publish_event for: `Worker.create` err: %s", exc)
        log.info("exiting post_worker_create_cache_worker")

    @hook_ctx(ops="create", phase="POST_COMMIT")
    async def _post_create_auto_register(cls, ctx):
        from peagen.gateway import authn_adapter, log

        log.info("entering post_worker_create_auto_register")
        created = cls.schemas.read.out.model_validate(
            ctx["result"], from_attributes=True
        )
        try:
            base = authn_adapter.base_url

            def _tenant_id(session):
                pool = session.get(Pool, created.pool_id)
                return str(pool.tenant_id) if pool else None

            tenant_id = await ctx["db"].run_sync(_tenant_id)

            svc_resp = await authn_adapter._client.post(
                f"{base}/service",
                json={"name": f"worker-{created.id}", "tenant_id": tenant_id},
            )
            svc_resp.raise_for_status()
            service_id = svc_resp.json()["id"]
            key_resp = await authn_adapter._client.post(
                f"{base}/servicekey",
                json={
                    "service_id": service_id,
                    "label": "worker",
                },
            )
            key_resp.raise_for_status()
            body = key_resp.json()
            ctx["raw_worker_key"] = body.get("api_key")
            log.info("auto-registration succeeded for worker %s", created.id)
        except Exception as exc:  # pragma: no cover
            log.error("auto-registration failed: %s", exc)
            ctx["raw_worker_key"] = None
        log.info("exiting post_worker_create_auto_register")

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    async def _post_create_inject_key(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_worker_create_inject_key")
        raw = ctx.get("raw_worker_key")
        if not raw:
            log.info("no worker key to inject; exiting post_worker_create_inject_key")
            return

        res = ctx.get("result")
        if res is None:
            log.info("no result payload; exiting post_worker_create_inject_key")
            return

        # Normalize ctx["result"] -> plain dict
        if isinstance(res, dict):
            out = dict(res)  # copy
        elif hasattr(res, "model_dump"):  # Pydantic model
            out = res.model_dump(mode="json")
        else:  # ORM instance
            out = cls.schemas.read.out.model_validate(
                res, from_attributes=True
            ).model_dump(mode="json")

        # Inject the key into the response payload only (not persisted)
        out["api_key"] = raw
        log.info("injected worker key into response for worker %s", out.get("id"))

        ctx["result"] = out
        resp = ctx.get("response")
        if resp is not None:
            resp.result = out
        log.info("exiting post_worker_create_inject_key")

    @hook_ctx(ops="update", phase="PRE_TX_BEGIN")
    async def _pre_update_policy_gate(cls, ctx):
        from peagen.gateway import log

        log.info("entering pre_worker_update_policy_gate")
        wu = ctx["env"].params
        worker_id = str(wu["id"] or wu["item_id"])
        pool_id = wu.get("pool_id")
        if pool_id is None:
            from peagen.gateway import queue

            pool_id = await queue.hget(WORKER_KEY.format(worker_id), "pool_id")
        if isinstance(pool_id, str):
            pool_id = UUID(pool_id)

        ip = cls._client_ip(ctx["request"])

        def _get_policy_and_count(session):
            pool = session.get(Pool, pool_id)
            count = session.query(cls).filter(cls.pool_id == pool_id).count()
            return (pool.policy if pool else {}, count)

        policy, count = await ctx["db"].run_sync(_get_policy_and_count)
        log.info(
            "loaded pool policy %s with %s existing workers for pool %s",
            policy,
            count,
            pool_id,
        )
        cls._check_pool_policy(policy or {}, ip, count)
        log.info("exiting pre_worker_update_policy_gate")

    @hook_ctx(ops="update", phase="PRE_TX_BEGIN")
    async def _pre_update(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.transport.jsonrpc import RPCException

        log.info("entering pre_worker_update")
        wu = ctx["env"].params
        worker_id = str(wu["id"] or wu["item_id"])
        cached = await queue.exists(WORKER_KEY.format(worker_id))
        if not cached and wu["pool_id"] is None:
            log.info(
                "worker %s not cached and no pool_id provided; raising RPCException",
                worker_id,
            )
            raise RPCException(code=-32602, message="unknown worker; pool_id required")
        ctx["worker_id"] = worker_id
        log.info("exiting pre_worker_update")

    @hook_ctx(ops="update", phase="POST_RESPONSE")
    async def _post_update_cache_pool(cls, ctx):
        from peagen.gateway import log, queue

        log.info("entering post_worker_update_cache_pool")
        worker_id = ctx["worker_id"]
        updated = None
        try:
            updated = cls.schemas.read.out.model_validate(
                ctx["result"], from_attributes=True
            )
            if updated.pool_id:
                await queue.sadd(f"pool_id:{updated.pool_id}:members", worker_id)
                log.info("cached member `%s` in `%s`", worker_id, updated.pool_id)
            else:
                log.info("worker %s has no pool_id to cache", worker_id)
        except Exception as exc:  # noqa: BLE001
            log.info(
                "pool member `%s` failed to cache in `%s` err: %s",
                worker_id,
                getattr(updated, "pool_id", ""),
                exc,
            )
        log.info("exiting post_worker_update_cache_pool")

    @hook_ctx(ops="update", phase="POST_RESPONSE")
    async def _post_update_cache_worker(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_event

        log.info("entering post_worker_update_cache_worker")
        worker_id = ctx["worker_id"]
        updated = None
        try:
            updated = cls.schemas.read.out.model_validate(
                ctx["result"], from_attributes=True
            )
            key = WORKER_KEY.format(worker_id)
            await queue.hset(key, {"updated_at": str(updated.updated_at)})
            await queue.expire(key, WORKER_TTL)
            log.info("cached worker: `%s`", worker_id)
        except Exception as exc:  # noqa: BLE001
            log.info("cached failed for worker: `%s` err: %s", worker_id, exc)
        try:
            await _publish_event(queue, "Worker.update", updated)
            log.info("published Worker.update event for %s", worker_id)
        except Exception as exc:  # noqa: BLE001
            log.error("failure to _publish_event for: `Worker.update` err: %s", exc)
        log.info("exiting post_worker_update_cache_worker")


    @hook_ctx(ops="delete", phase="POST_HANDLER")
    async def _post_delete(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_event

        log.info("entering post_worker_delete")
        wu = ctx["env"].params
        worker_id = str(wu["id"] or wu["item_id"])
        try:
            await queue.expire(WORKER_KEY.format(worker_id), 0)
            log.info("worker expired: `%s`", worker_id)
        except Exception as exc:  # noqa: BLE001
            log.info("worker expiration op failed: `%s` err: %s", worker_id, exc)
        try:
            await _publish_event(queue, "Worker.delete", {"id": worker_id})
            log.info("published Worker.delete event for %s", worker_id)
        except Exception as exc:  # noqa: BLE001
            log.info("failure to _publish_event for: `Worker.delete` err: %s", exc)
        log.info("exiting post_worker_delete")

        # hooks registered via @hook_ctx


__all__ = ["Worker"]
