from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    ArtefactLineage,
    FanoutSet,
    StatusLog,
    TaskRevision,
    asdict,
)
from .errors import PeagenError, PeagenHashMismatchError


async def _execute_insert(session: AsyncSession, stmt: str, params: dict[str, Any]) -> None:
    try:
        await session.execute(text(stmt), params)
    except IntegrityError as exc:  # duplicate key or FK violation
        raise PeagenError(str(exc)) from exc


async def insert_task_revision(session: AsyncSession, row: TaskRevision) -> None:
    if row.parent_hash:
        res = await session.execute(
            text("SELECT 1 FROM task_revision WHERE rev_hash = :h"),
            {"h": row.parent_hash},
        )
        if res.scalar() is None:
            raise PeagenHashMismatchError(f"parent hash {row.parent_hash} not found")

    stmt = (
        "INSERT INTO task_revision (rev_hash, task_id, parent_hash, ts_created) "
        "VALUES (:rev_hash, :task_id, :parent_hash, :ts_created)"
    )
    await _execute_insert(session, stmt, asdict(row))


async def insert_artefact_lineage(session: AsyncSession, row: ArtefactLineage) -> None:
    stmt = (
        "INSERT INTO artefact_lineage (edge_hash, parent_hash, child_hash, ts_logged) "
        "VALUES (:edge_hash, :parent_hash, :child_hash, :ts_logged)"
    )
    await _execute_insert(session, stmt, asdict(row))


async def insert_fanout_set(session: AsyncSession, row: FanoutSet) -> None:
    stmt = (
        "INSERT INTO fanout_set (rev_hash, child_hash, ts_logged) "
        "VALUES (:rev_hash, :child_hash, :ts_logged)"
    )
    await _execute_insert(session, stmt, asdict(row))


async def insert_status_log(session: AsyncSession, row: StatusLog) -> None:
    stmt = (
        "INSERT INTO status_log (rev_hash, status, ts_logged) "
        "VALUES (:rev_hash, :status, :ts_logged)"
    )
    await _execute_insert(session, stmt, asdict(row))
