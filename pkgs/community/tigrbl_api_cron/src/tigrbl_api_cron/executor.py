"""Utilities to execute registered cron jobs and persist their results."""

from __future__ import annotations

import dataclasses
import datetime as dt
import inspect
from collections.abc import Sequence
from typing import Any, TYPE_CHECKING

from croniter import CroniterBadCronError, croniter_range
from sqlalchemy.ext.asyncio import AsyncSession

from tigrbl.orm.mixins.utils import tzutcnow

from .registry import get_handler
from .tables import CronJob, CronJobResult

if TYPE_CHECKING:  # pragma: no cover - import for typing only
    from tigrbl import TigrblApp

_JSON_NATIVE = (dict, list, str, int, float, bool, type(None))


def _ensure_aware(value: dt.datetime | None) -> dt.datetime | None:
    """Ensure a datetime is timezone-aware using UTC when missing."""

    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.timezone.utc)
    return value


def _normalize_payload(value: Any) -> Any:
    """Normalize handler return values into JSON-compatible payloads."""

    if isinstance(value, _JSON_NATIVE):
        return value
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "model_dump") and callable(value.model_dump):
        try:
            return value.model_dump()
        except Exception:  # pragma: no cover - best effort
            pass
    if hasattr(value, "dict") and callable(value.dict):
        try:
            return value.dict()
        except Exception:  # pragma: no cover - best effort
            pass
    return {"value": repr(value)}


def _resolve_due_at(job: CronJob, *, now: dt.datetime) -> dt.datetime | None:
    """Return the most recent scheduled execution time that has not run yet."""

    valid_from = _ensure_aware(job.valid_from)
    valid_to = _ensure_aware(job.valid_to)
    last_run = _ensure_aware(job.last_run_at)

    assert valid_from is not None  # mixin defaults ensure presence

    if now < valid_from:
        return None
    if valid_to is not None and now > valid_to:
        return None

    start = last_run or valid_from
    occurrences: list[dt.datetime] = []
    for occurrence in croniter_range(
        start,
        now,
        job.cron_expression,
        ret_type=dt.datetime,
    ):
        if last_run is None or occurrence > last_run:
            occurrences.append(occurrence)
    if not occurrences:
        return None
    candidate = occurrences[-1]
    if candidate < valid_from:
        return None
    if valid_to is not None and candidate > valid_to:
        return None
    return candidate


async def _invoke(
    handler,
    *,
    job: CronJob,
    session: AsyncSession,
    scheduled_for: dt.datetime,
    now: dt.datetime,
) -> Any:
    """Invoke a cron handler, awaiting coroutines when necessary."""

    result = handler(job=job, session=session, scheduled_for=scheduled_for, now=now)
    if inspect.isawaitable(result):  # pragma: no branch - simple predicate
        return await result
    return result


async def _record_result(
    *,
    session: AsyncSession,
    job: CronJob,
    status: str,
    scheduled_for: dt.datetime,
    started_at: dt.datetime,
    payload: Any = None,
    error: str | None = None,
) -> CronJobResult:
    """Persist a :class:`CronJobResult` row and mirror state on the job."""

    payload_data = {
        "cron_job_id": job.id,
        "status": status,
        "scheduled_for": scheduled_for,
        "started_at": started_at,
        "finished_at": tzutcnow(),
    }
    if payload is not None:
        payload_data["result_payload"] = _normalize_payload(payload)
    if error is not None:
        payload_data["error_message"] = error

    record = await CronJobResult.handlers.create.core(
        {"payload": payload_data, "db": session}
    )

    job.last_run_at = scheduled_for
    job.last_status = status
    job.last_error = error
    await session.flush()

    return record


async def execute_due_jobs(
    app: "TigrblApp",
    *,
    now: dt.datetime | None = None,
    limit: int | None = None,
) -> Sequence[CronJobResult]:
    """Execute cron jobs that are due at ``now`` and record their results."""

    current_time = now or tzutcnow()
    results: list[CronJobResult] = []

    async with app.engine.asession() as session:
        filter_payload = {
            "filters": {
                "valid_from__lte": current_time,
            },
            "sort": [
                {"field": "created_at", "direction": "asc"},
            ],
        }
        jobs = await CronJob.handlers.list.core(
            {"db": session, "payload": filter_payload}
        )

        for job in jobs:
            if limit is not None and len(results) >= limit:
                break

            try:
                scheduled_for = _resolve_due_at(job, now=current_time)
            except CroniterBadCronError as exc:
                record = await _record_result(
                    session=session,
                    job=job,
                    status="failed",
                    scheduled_for=current_time,
                    started_at=current_time,
                    payload=None,
                    error=f"Invalid cron expression: {exc}",
                )
                results.append(record)
                continue

            if scheduled_for is None:
                continue

            handler = get_handler(job.pkg_uid)
            if handler is None:
                record = await _record_result(
                    session=session,
                    job=job,
                    status="skipped",
                    scheduled_for=scheduled_for,
                    started_at=current_time,
                    payload=None,
                    error=f"No handler registered for '{job.pkg_uid}'",
                )
                results.append(record)
                continue

            try:
                job.last_status = "running"
                job.last_error = None
                await session.flush()
                outcome = await _invoke(
                    handler,
                    job=job,
                    session=session,
                    scheduled_for=scheduled_for,
                    now=current_time,
                )
                record = await _record_result(
                    session=session,
                    job=job,
                    status="success",
                    scheduled_for=scheduled_for,
                    started_at=current_time,
                    payload=outcome,
                    error=None,
                )
            except Exception as exc:  # pragma: no cover - error path depends on handler
                record = await _record_result(
                    session=session,
                    job=job,
                    status="failed",
                    scheduled_for=scheduled_for,
                    started_at=current_time,
                    payload=None,
                    error=str(exc),
                )
            results.append(record)

        await session.commit()

    return results


__all__ = ["execute_due_jobs"]
