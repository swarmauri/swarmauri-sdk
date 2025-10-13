"""Result records for cron job executions."""

from __future__ import annotations

import datetime as dt

from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.table import Base
from tigrbl.types import JSON, Mapped, PgUUID, String, TZDateTime, UUID


class CronJobResult(Base, GUIDPk, Timestamped):
    """Execution outcome for a :class:`CronJob`."""

    __tablename__ = "cron_job_results"

    cron_job_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="cron_jobs.id", on_delete="CASCADE"),
                nullable=False,
            ),
            field=F(py_type=UUID),
            io=IO(out_verbs=("read", "list")),
        )
    )
    status: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(
                py_type=str,
                constraints={
                    "enum": ["running", "success", "failed", "skipped"],
                },
            ),
            io=IO(out_verbs=("read", "list")),
        )
    )
    scheduled_for: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(out_verbs=("read", "list")),
        )
    )
    started_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(out_verbs=("read", "list")),
        )
    )
    finished_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime | None),
            io=IO(out_verbs=("read", "list")),
        )
    )
    result_payload: Mapped[dict | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSON, nullable=True),
            field=F(py_type=dict | None),
            io=IO(out_verbs=("read", "list")),
        ),
        name="result",
    )
    error_message: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None),
            io=IO(out_verbs=("read", "list")),
        )
    )


__all__ = ["CronJobResult"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__() -> list[str]:
    return sorted(__all__)
