from __future__ import annotations

from autoapi.v3.orm.tables import Base
from autoapi.v3.types import (
    JSON,
    PgUUID,
    Integer,
    relationship,
    HookProvider,
    Mapped,
)
from autoapi.v3.orm.mixins import GUIDPk, Timestamped, StatusColumn
from autoapi.v3.specs import S, acol
from autoapi.v3.specs.storage_spec import ForeignKeySpec
from autoapi.v3 import hook_ctx
from typing import TYPE_CHECKING

from .tasks import Task

if TYPE_CHECKING:  # pragma: no cover
    from .eval_result import EvalResult


class Work(Base, GUIDPk, Timestamped, StatusColumn, HookProvider):
    __tablename__ = "works"
    __table_args__ = ({"schema": "peagen"},)
    task_id: Mapped[PgUUID] = acol(
        storage=S(
            PgUUID(as_uuid=True), fk=ForeignKeySpec("peagen.tasks.id"), nullable=False
        )
    )
    result: Mapped[dict | None] = acol(storage=S(JSON, nullable=True))
    duration_s: Mapped[int | None] = acol(storage=S(Integer))

    task: Mapped[Task] = relationship(Task, back_populates="works")
    eval_results: Mapped[list["EvalResult"]] = relationship(
        "EvalResult",
        back_populates="work",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @hook_ctx(ops="update", phase="POST_COMMIT")
    async def _post_update(cls, ctx):
        from peagen.gateway import log, queue
        from peagen.gateway._publish import _publish_task
        from peagen.gateway.schedule_helpers import (
            _finalize_parent_tasks,
            _load_task,
            _save_task,
        )
        from peagen.orm import Status

        log.info("entering post_work_update")
        wr = cls.schemas.read.out.model_validate(ctx["result"], from_attributes=True)
        if not Status.is_terminal(wr.status):
            return
        task = await _load_task(queue, str(wr.task_id))
        if task is None:
            log.warning("terminal Work for unknown Task %s", wr.task_id)
            return
        updated = task.model_copy(
            update={
                "status": wr.status,
                "result": wr.result or {},
                "last_modified": wr.last_modified,
            }
        )
        await _save_task(queue, updated)
        await _publish_task(updated.model_dump(mode="json"))
        await _finalize_parent_tasks(queue, str(wr.task_id))
        log.info("Task %s closed via Work %s → %s", wr.task_id, wr.id, wr.status)

        # hooks registered via @hook_ctx


__all__ = ["Work"]
