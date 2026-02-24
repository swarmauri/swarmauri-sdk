"""Cron job model definition."""

from __future__ import annotations

import datetime as dt

from tigrbl.orm.mixins import GUIDPk, Timestamped, ValidityWindow
from tigrbl.orm.mixins.utils import CRUD_IO
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.table import Base
from tigrbl.types import JSON, Mapped, String, TZDateTime, UniqueConstraint


class CronJob(Base, GUIDPk, Timestamped, ValidityWindow):
    """Cron schedule that references a registered package UID."""

    __tablename__ = "cron_jobs"

    pkg_uid: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False, unique=True, index=True),
            field=F(py_type=str, constraints={"min_length": 1}),
            io=CRUD_IO,
        )
    )
    cron_expression: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(
                py_type=str,
                constraints={
                    "min_length": 3,
                    "examples": ["*/5 * * * *", "0 0 * * 0"],
                },
            ),
            io=CRUD_IO,
        )
    )
    payload: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSON, default=dict, nullable=False),
            field=F(py_type=dict),
            io=CRUD_IO,
        )
    )
    last_run_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime | None),
            io=IO(out_verbs=("read", "list")),
        )
    )
    last_status: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, default="never", nullable=False),
            field=F(
                py_type=str,
                constraints={
                    "enum": ["never", "running", "success", "failed", "skipped"],
                },
            ),
            io=IO(out_verbs=("read", "list")),
        )
    )
    last_error: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None),
            io=IO(out_verbs=("read", "list")),
        )
    )

    __table_args__ = (UniqueConstraint("pkg_uid", name="uq_cron_jobs_pkg_uid"),)


__all__ = ["CronJob"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__() -> list[str]:
    return sorted(__all__)
