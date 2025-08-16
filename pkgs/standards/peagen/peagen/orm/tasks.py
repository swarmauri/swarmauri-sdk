from __future__ import annotations

import json
from enum import Enum, auto

from autoapi.v2.types import (
    JSON,
    Column,
    String,
    PgEnum,
    PgUUID,
    Integer,
    ForeignKey,
    relationship,
    HookProvider,
)
from autoapi.v2.tables import Base
from autoapi.v2.mixins import (
    GUIDPk,
    Timestamped,
    TenantBound,
    Ownable,
    StatusMixin,
)
from peagen.orm.mixins import RepositoryRefMixin


class Action(str, Enum):
    INIT = auto()
    SORT = auto()
    PROCESS = auto()
    MUTATE = auto()
    EVOLVE = auto()
    FETCH = auto()
    VALIDATE = auto()


class SpecKind(str, Enum):
    DOE = "doe"
    EVOLVE = "evolve"
    PAYLOAD = "payload"


class Task(
    Base,
    GUIDPk,
    Timestamped,
    TenantBound,
    Ownable,
    RepositoryRefMixin,
    StatusMixin,
    HookProvider,
):
    __tablename__ = "tasks"
    __table_args__ = ({"schema": "peagen"},)
    action = Column(PgEnum(Action, name="task_action"), nullable=False)
    pool_id = Column(
        PgUUID(as_uuid=True), ForeignKey("peagen.pools.id"), nullable=False
    )
    config_toml = Column(String)
    spec_kind = Column(PgEnum(SpecKind, name="task_spec_kind"), nullable=True)
    spec_uuid = Column(PgUUID(as_uuid=True), nullable=True)
    args = Column(JSON, nullable=False, default=dict)
    labels = Column(JSON, nullable=False, default=dict)
    note = Column(String)
    schema_version = Column(Integer, nullable=False, default=3)

    works = relationship("Work", back_populates="task")

    @classmethod
    async def _pre_create(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway.schedule_helpers import get_live_workers_by_pool
        from peagen.transport.jsonrpc import RPCException
        from peagen._utils._split_github import _split_github
        from peagen.core.git_shadow_core import (
            attach_deploy_key,
            ensure_mirror,
            ensure_org,
        )

        log.info("entering pre_task_create")
        tc = ctx["env"].params
        args = tc.args or {}
        repo_url = args.get("repo_url")
        deploy_key = args.get("deploy_key")
        if repo_url and deploy_key:
            try:
                org, repo = _split_github(repo_url)
                slug = org.lower()
                await ensure_org(slug)
                await ensure_mirror(slug, repo, repo_url)
                key_id = await attach_deploy_key(slug, repo, deploy_key, rw=True)
                args["deploy_key_id"] = key_id
                tc = tc.model_copy(update={"args": args})
            except Exception as exc:  # noqa: BLE001
                log.error("shadow-repo setup failed: %s", exc, exc_info=True)
                raise RPCException(code=-32011, message="shadow-repo setup error")
        action = tc.action
        if action:
            advertised = {
                h
                for w in await get_live_workers_by_pool(queue, tc.pool_id)
                for h in (
                    json.loads(w.get("handlers", "[]"))
                    if isinstance(w.get("handlers"), str)
                    else w.get("handlers", [])
                )
            }
            if action not in advertised:
                log.warning("no worker advertising '%s' found", action)
        ctx["task_in"] = tc

    @classmethod
    async def _post_create(cls, ctx):
        from peagen.defaults import READY_QUEUE, TASK_TTL
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_queue_length, _publish_task
        from peagen.gateway.schedule_helpers import _save_task

        log.info("entering post_task_create")
        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        submitted = ctx["task_in"]
        wire = submitted.model_copy(update={"id": created.id})
        await queue.rpush(
            f"{READY_QUEUE}:{wire.pool_id}",
            json.dumps(wire.model_dump(mode="json")),
        )
        await queue.sadd("pools", wire.pool_id)
        await _publish_queue_length(queue, wire.pool_id)
        await _save_task(queue, cls._SRead.model_validate(wire.model_dump()))
        await _publish_task(wire.model_dump())
        log.info("task %s queued in %s (ttl=%s)", created.id, wire.pool_id, TASK_TTL)

    @classmethod
    async def _pre_update(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway.schedule_helpers import _load_task
        from peagen.errors import TaskNotFoundError

        log.info("entering pre_task_update")
        upd = ctx["env"].params
        tid = upd.id or upd.item_id
        cached = await _load_task(queue, tid)
        if cached is None:
            raise TaskNotFoundError(tid)
        ctx["cached_task"] = cached
        ctx["changes"] = upd.model_dump(exclude_unset=True)

    @classmethod
    async def _post_update(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_task
        from peagen.gateway.schedule_helpers import _finalize_parent_tasks, _save_task

        log.info("entering post_task_update")
        task = ctx["cached_task"]
        changes = ctx["changes"]
        task = task.model_copy(update=changes)
        await _save_task(queue, task)
        await _publish_task(task.model_dump())
        if isinstance(changes.get("result"), dict):
            for cid in changes["result"].get("children", []):
                await _finalize_parent_tasks(queue, cid)
        log.info("task %s updated (%s)", task.id, ", ".join(changes))

    @classmethod
    async def _pre_read(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway.schedule_helpers import _load_task

        log.info("entering pre_task_read")
        tid = ctx["env"].params.get("id") or ctx["env"].params.get("item_id")
        hit = await _load_task(queue, tid)
        if hit:
            ctx["cached_task"] = hit
            ctx["skip_db"] = True

    @classmethod
    async def _post_read(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_task_read")
        if ctx.get("skip_db") and ctx.get("cached_task"):
            ctx["result"] = ctx["cached_task"]

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import Phase, get_schema

        cls._SCreate = get_schema(cls, "create")
        cls._SRead = get_schema(cls, "read")
        cls._SUpdate = get_schema(cls, "update")
        model_name = cls.__name__
        api.register_hook(Phase.PRE_TX_BEGIN, model=model_name, op="create")(
            cls._pre_create
        )
        api.register_hook(Phase.PRE_TX_BEGIN, model=model_name, op="update")(
            cls._pre_update
        )
        api.register_hook(Phase.PRE_TX_BEGIN, model=model_name, op="read")(cls._pre_read)
        api.register_hook(Phase.POST_COMMIT, model=model_name, op="create")(
            cls._post_create
        )
        api.register_hook(Phase.POST_COMMIT, model=model_name, op="update")(
            cls._post_update
        )
        api.register_hook(Phase.POST_HANDLER, model=model_name, op="read")(cls._post_read)


__all__ = ["Action", "SpecKind", "Task"]
