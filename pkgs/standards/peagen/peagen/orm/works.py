from __future__ import annotations

from autoapi.v3.types import (
    JSON,
    Column,
    PgUUID,
    Integer,
    ForeignKey,
    relationship,
    HookProvider,
)
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped, StatusMixin

from .tasks import Task


class Work(Base, GUIDPk, Timestamped, StatusMixin, HookProvider):
    __tablename__ = "works"
    __table_args__ = ({"schema": "peagen"},)
    task_id = Column(
        PgUUID(as_uuid=True), ForeignKey("peagen.tasks.id"), nullable=False
    )
    result = Column(JSON, nullable=True)
    duration_s = Column(Integer)

    task = relationship(Task, back_populates="works")
    eval_results = relationship(
        "EvalResult",
        back_populates="work",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @classmethod
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
        wr = cls._SRead.model_validate(ctx["result"], from_attributes=True)
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

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v3 import _schema

        cls._SRead = _schema(cls, verb="read")
        api.register_hook("POST_COMMIT", model="Work", op="update")(cls._post_update)


__all__ = ["Work"]
