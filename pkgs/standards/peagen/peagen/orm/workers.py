from __future__ import annotations


from autoapi.v2.types import (
    JSON,
    Column,
    ForeignKey,
    PgUUID,
    UUID,
    String,
    MutableDict,
    relationship,
    HookProvider,
    AllowAnonProvider,
)
from autoapi.v2.tables import Base

from autoapi.v2.mixins import GUIDPk, Timestamped
from peagen.defaults import DEFAULT_POOL_ID, WORKER_KEY, WORKER_TTL

from .pools import Pool


class Worker(Base, GUIDPk, Timestamped, HookProvider, AllowAnonProvider):
    __tablename__ = "workers"
    pool_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("pools.id"),
        nullable=False,
        default=DEFAULT_POOL_ID,
    )
    url = Column(String, nullable=False, info=dict(no_update=True))
    advertises = Column(
        MutableDict.as_mutable(JSON),  # or JSON
        default=lambda: {},  # ✔ correct for SQLAlchemy
        nullable=True,
        info=dict(no_update=True),
    )
    handlers = Column(
        MutableDict.as_mutable(JSON),  # or JSON
        default=lambda: {},  # ✔ correct for SQLAlchemy
        nullable=True,
        info=dict(no_update=True),
    )

    pool = relationship(Pool, backref="workers")

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

    # ─── AutoAPI hook callbacks ------------------------------------------
    @classmethod
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
        cls._check_pool_policy(policy or {}, ip, count)

    @classmethod
    async def _post_create_cache_pool(cls, ctx):
        from peagen.gateway import log, queue

        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        log.info("worker %s joined pool_id %s", created.id, created.pool_id)
        try:
            await queue.sadd(f"pool_id:{created.pool_id}:members", str(created.id))
        except Exception as exc:  # noqa: BLE001
            log.error("failure to add member to pool queue. err: %s", exc)

    @classmethod
    async def _post_create_cache_worker(cls, ctx):
        from peagen.gateway import log, queue

        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        try:
            key = WORKER_KEY.format(str(created.id))
            await queue.hset(key, cls._as_redis_hash(created))
            await queue.expire(key, WORKER_TTL)
            log.info("cached `%s`", key)
        except Exception as exc:  # noqa: BLE001
            log.error("failure to add worker. err: %s", exc)
        try:
            from peagen.gateway._publish import _publish_event

            await _publish_event(queue, "Workers.create", created)
        except Exception as exc:  # noqa: BLE001
            log.error("failure to _publish_event for: `Workers.create` err: %s", exc)

    @classmethod
    async def _post_create_auto_register(cls, ctx):
        from peagen.gateway import authn_adapter, log

        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        try:
            base = authn_adapter.base_url

            def _tenant_id(session):
                pool = session.get(Pool, created.pool_id)
                return str(pool.tenant_id) if pool else None

            tenant_id = await ctx["db"].run_sync(_tenant_id)

            svc_resp = await authn_adapter._client.post(
                f"{base}/services",
                json={"name": f"worker-{created.id}", "tenant_id": tenant_id},
            )
            svc_resp.raise_for_status()
            service_id = svc_resp.json()["id"]
            key_resp = await authn_adapter._client.post(
                f"{base}/service_keys",
                json={
                    "service_id": service_id,
                    "label": "worker",
                },
            )
            key_resp.raise_for_status()
            body = key_resp.json()
            ctx["raw_worker_key"] = body.get("api_key")
        except Exception as exc:  # pragma: no cover
            log.error("auto-registration failed: %s", exc)
            ctx["raw_worker_key"] = None

    @classmethod
    async def _post_create_inject_key(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_worker_create_inject_key")
        raw = ctx.get("raw_worker_key")
        if not raw:
            return
        result = dict(ctx.get("result", {}))
        result["api_key"] = raw
        ctx["result"] = result
        resp = ctx.get("response")
        if resp is not None:
            resp.result = result

    @classmethod
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
        cls._check_pool_policy(policy or {}, ip, count)

    @classmethod
    async def _pre_update(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.transport.jsonrpc import RPCException

        log.info("entering pre_worker_update")
        wu = ctx["env"].params
        worker_id = str(wu["id"] or wu["item_id"])
        cached = await queue.exists(WORKER_KEY.format(worker_id))
        if not cached and wu["pool_id"] is None:
            raise RPCException(code=-32602, message="unknown worker; pool_id required")
        ctx["worker_id"] = worker_id

    @classmethod
    async def _post_update_cache_pool(cls, ctx):
        from peagen.gateway import log, queue

        worker_id = ctx["worker_id"]
        try:
            updated = cls._SRead.model_validate(ctx["result"], from_attributes=True)
            if updated.pool_id:
                await queue.sadd(f"pool_id:{updated.pool_id}:members", worker_id)
            log.info("cached member `%s` in `%s`", worker_id, updated.pool_id)
        except Exception as exc:  # noqa: BLE001
            log.info(
                "pool member `%s` failed to cache in `%s` err: %s",
                worker_id,
                getattr(updated, "pool_id", ""),
                exc,
            )

    @classmethod
    async def _post_update_cache_worker(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_event

        worker_id = ctx["worker_id"]
        try:
            updated = cls._SRead.model_validate(ctx["result"], from_attributes=True)
            key = WORKER_KEY.format(worker_id)
            await queue.hset(key, {"updated_at": str(updated.updated_at)})
            await queue.expire(key, WORKER_TTL)
            log.info("cached worker: `%s`", worker_id)
        except Exception as exc:  # noqa: BLE001
            log.info("cached failed for worker: `%s` err: %s", worker_id, exc)
        try:
            await _publish_event(queue, "Worker.update", updated)
        except Exception as exc:  # noqa: BLE001
            log.error("failure to _publish_event for: `Worker.update` err: %s", exc)

    @classmethod
    async def _post_list(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_workers_list")

    @classmethod
    async def _post_delete(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_event

        wu = ctx["env"].params
        worker_id = str(wu["id"] or wu["item_id"])
        try:
            await queue.expire(WORKER_KEY.format(worker_id), 0)
            log.info("worker expired: `%s`", worker_id)
        except Exception as exc:  # noqa: BLE001
            log.info("worker expiration op failed: `%s` err: %s", worker_id, exc)
        try:
            await _publish_event(queue, "Worker.delete", {"id": worker_id})
        except Exception as exc:  # noqa: BLE001
            log.info("failure to _publish_event for: `Worker.delete` err: %s", exc)

    @classmethod
    def __autoapi_allow_anon__(cls) -> set[str]:
        return {"create"}

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import Phase, AutoAPI

        cls._SRead = AutoAPI.get_schema(cls, "read")
        api.register_hook(Phase.PRE_TX_BEGIN, model="Worker", op="create")(
            cls._pre_create_policy_gate
        )
        api.register_hook(Phase.POST_RESPONSE, model="Worker", op="create")(
            cls._post_create_cache_pool
        )
        api.register_hook(Phase.POST_RESPONSE, model="Worker", op="create")(
            cls._post_create_cache_worker
        )
        api.register_hook(Phase.POST_COMMIT, model="Worker", op="create")(
            cls._post_create_auto_register
        )
        api.register_hook(Phase.POST_RESPONSE, model="Worker", op="create")(
            cls._post_create_inject_key
        )
        api.register_hook(Phase.PRE_TX_BEGIN, model="Worker", op="update")(
            cls._pre_update_policy_gate
        )
        api.register_hook(Phase.PRE_TX_BEGIN, model="Worker", op="update")(
            cls._pre_update
        )
        api.register_hook(Phase.POST_RESPONSE, model="Worker", op="update")(
            cls._post_update_cache_pool
        )
        api.register_hook(Phase.POST_RESPONSE, model="Worker", op="update")(
            cls._post_update_cache_worker
        )
        api.register_hook(Phase.POST_HANDLER, model="Worker", op="list")(cls._post_list)
        api.register_hook(Phase.POST_HANDLER, model="Worker", op="delete")(
            cls._post_delete
        )


__all__ = ["Worker"]
