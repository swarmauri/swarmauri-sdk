from __future__ import annotations

import json
from enum import Enum, auto

from autoapi.v3.orm.tables import Base
from autoapi.v3.types import (
    JSON,
    String,
    PgEnum,
    PgUUID,
    Integer,
    relationship,
    Mapped,
)
from autoapi.v3.orm.mixins import (
    GUIDPk,
    Timestamped,
    TenantBound,
    Ownable,
    StatusColumn,
)
from autoapi.v3.specs import S, acol
from autoapi.v3.column.storage_spec import ForeignKeySpec
from autoapi.v3 import hook_ctx
from autoapi.v3.bindings import build_schemas as _build_schemas
from typing import TYPE_CHECKING
from peagen.orm.mixins import RepositoryRefMixin

if TYPE_CHECKING:  # pragma: no cover
    from .works import Work


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
    StatusColumn,
):
    __tablename__ = "tasks"
    __table_args__ = ({"schema": "peagen"},)
    action: Mapped[Action] = acol(
        storage=S(PgEnum(Action, name="task_action"), nullable=False)
    )
    pool_id: Mapped[PgUUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec("peagen.pools.id"),
            nullable=False,
        )
    )
    config_toml: Mapped[str | None] = acol(storage=S(String))
    spec_kind: Mapped[SpecKind | None] = acol(
        storage=S(PgEnum(SpecKind, name="task_spec_kind"), nullable=True)
    )
    spec_uuid: Mapped[PgUUID | None] = acol(
        storage=S(PgUUID(as_uuid=True), nullable=True)
    )
    args: Mapped[dict] = acol(storage=S(JSON, nullable=False, default=dict))
    labels: Mapped[dict] = acol(storage=S(JSON, nullable=False, default=dict))
    note: Mapped[str | None] = acol(storage=S(String))
    schema_version: Mapped[int] = acol(storage=S(Integer, nullable=False, default=3))

    works: Mapped[list["Work"]] = relationship("Work", back_populates="task")

    @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
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

    @hook_ctx(ops="create", phase="POST_COMMIT")
    async def _post_create(cls, ctx):
        from peagen.defaults import READY_QUEUE, TASK_TTL
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_queue_length, _publish_task
        from peagen.gateway.schedule_helpers import _save_task

        log.info("entering post_task_create")
        created = cls.schemas.read.out.model_validate(
            ctx["result"], from_attributes=True
        )
        submitted = ctx["task_in"]
        wire = submitted.model_copy(update={"id": created.id})
        await queue.rpush(
            f"{READY_QUEUE}:{wire.pool_id}",
            json.dumps(wire.model_dump(mode="json")),
        )
        await queue.sadd("pools", wire.pool_id)
        await _publish_queue_length(queue, wire.pool_id)
        await _save_task(queue, cls.schemas.read.out.model_validate(wire.model_dump()))
        await _publish_task(wire.model_dump())
        log.info("task %s queued in %s (ttl=%s)", created.id, wire.pool_id, TASK_TTL)

    @hook_ctx(ops="update", phase="PRE_TX_BEGIN")
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

    @hook_ctx(ops="update", phase="POST_COMMIT")
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

    @hook_ctx(ops="read", phase="PRE_TX_BEGIN")
    async def _pre_read(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway.schedule_helpers import _load_task

        log.info("entering pre_task_read")
        tid = ctx["env"].params.get("id") or ctx["env"].params.get("item_id")
        hit = await _load_task(queue, tid)
        if hit:
            ctx["cached_task"] = hit
            ctx["skip_db"] = True

    @hook_ctx(ops="read", phase="POST_HANDLER")
    async def _post_read(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_task_read")
        if ctx.get("skip_db") and ctx.get("cached_task"):
            ctx["result"] = ctx["cached_task"]

        # hooks registered via @hook_ctx


__all__ = ["Action", "SpecKind", "Task"]

# Ensure the default "read" schemas are available for Task so that
# consumers referencing ``Task.schemas.read`` do not fail during import.
# ``Base`` normally builds CRUD schemas automatically, but some execution
# paths may omit the "read" op which then triggers a KeyError. Rebuilding
# the schema here guarantees the operation is registered.
if not hasattr(Task, "schemas") or not hasattr(Task.schemas, "read"):
    _build_schemas(Task, [], only_keys={"read"})
