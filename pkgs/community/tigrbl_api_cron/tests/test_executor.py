from __future__ import annotations

import datetime as dt

import httpx
import pytest

from tigrbl_api_cron import (
    build_app,
    clear_registry,
    execute_due_jobs,
    register_cron_job,
)


@pytest.fixture
async def cron_app():
    app = build_app(async_mode=True)
    await app.initialize()
    clear_registry()
    try:
        yield app
    finally:
        clear_registry()


@pytest.fixture
async def cron_client(cron_app):
    transport = httpx.ASGITransport(app=cron_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_execute_due_job_records_success(cron_app, cron_client):
    now = dt.datetime(2024, 1, 1, 12, 0, 30, tzinfo=dt.timezone.utc)

    @register_cron_job("demo.pkg")
    async def _handler(
        *, job, session, scheduled_for, now
    ):  # pragma: no cover - exercised indirectly
        return {"scheduled": scheduled_for.isoformat(), "invoked": now.isoformat()}

    create_payload = {
        "pkg_uid": "demo.pkg",
        "cron_expression": "* * * * *",
        "valid_from": (now - dt.timedelta(minutes=5)).isoformat(),
        "valid_to": (now + dt.timedelta(minutes=5)).isoformat(),
    }
    created = await cron_client.post("/cron/cronjob", json=create_payload)
    created.raise_for_status()
    job_id = created.json()["id"]

    results = await execute_due_jobs(cron_app, now=now)
    assert len(results) == 1
    record = results[0]
    assert record.status == "success"
    assert isinstance(record.result_payload, dict)
    assert record.result_payload["scheduled"] == record.scheduled_for.isoformat()

    stored = await cron_client.get(f"/cron/cronjob/{job_id}")
    stored.raise_for_status()
    data = stored.json()
    assert data["last_status"] == "success"
    last_run = dt.datetime.fromisoformat(data["last_run_at"])
    if last_run.tzinfo is None:
        last_run = last_run.replace(tzinfo=dt.timezone.utc)
    assert last_run == record.scheduled_for
    assert data["last_error"] is None

    listed = await cron_client.get("/cron/cronjobresult")
    listed.raise_for_status()
    results_payload = listed.json()
    assert len(results_payload) == 1
    assert results_payload[0]["status"] == "success"


@pytest.mark.asyncio
async def test_execute_due_job_handles_missing_handler(cron_app, cron_client):
    now = dt.datetime(2024, 1, 1, 12, 10, 0, tzinfo=dt.timezone.utc)
    create_payload = {
        "pkg_uid": "missing.handler",
        "cron_expression": "*/2 * * * *",
        "valid_from": (now - dt.timedelta(minutes=5)).isoformat(),
        "valid_to": (now + dt.timedelta(minutes=5)).isoformat(),
    }
    created = await cron_client.post("/cron/cronjob", json=create_payload)
    created.raise_for_status()
    job_id = created.json()["id"]

    results = await execute_due_jobs(cron_app, now=now)
    assert len(results) == 1
    record = results[0]
    assert record.status == "skipped"
    assert "No handler" in (record.error_message or "")

    stored = await cron_client.get(f"/cron/cronjob/{job_id}")
    stored.raise_for_status()
    payload = stored.json()
    assert payload["last_status"] == "skipped"
    assert "missing.handler" in (payload["last_error"] or "")

    listed = await cron_client.get("/cron/cronjobresult")
    listed.raise_for_status()
    assert listed.json()[0]["status"] == "skipped"


@pytest.mark.asyncio
async def test_invalid_cron_expression_records_failure(cron_app, cron_client):
    now = dt.datetime(2024, 1, 1, 12, 20, 0, tzinfo=dt.timezone.utc)
    create_payload = {
        "pkg_uid": "invalid.expr",
        "cron_expression": "not-a-cron",
        "valid_from": (now - dt.timedelta(minutes=5)).isoformat(),
        "valid_to": (now + dt.timedelta(minutes=5)).isoformat(),
    }
    created = await cron_client.post("/cron/cronjob", json=create_payload)
    created.raise_for_status()
    job_id = created.json()["id"]

    results = await execute_due_jobs(cron_app, now=now)
    assert len(results) == 1
    record = results[0]
    assert record.status == "failed"
    assert "Invalid cron expression" in (record.error_message or "")

    stored = await cron_client.get(f"/cron/cronjob/{job_id}")
    stored.raise_for_status()
    payload = stored.json()
    assert payload["last_status"] == "failed"
    assert "Invalid cron expression" in (payload["last_error"] or "")

    listed = await cron_client.get("/cron/cronjobresult")
    listed.raise_for_status()
    assert listed.json()[0]["status"] == "failed"


@pytest.mark.asyncio
async def test_execute_respects_limit(cron_app, cron_client):
    now = dt.datetime(2024, 1, 1, 12, 30, 0, tzinfo=dt.timezone.utc)

    @register_cron_job("limited.pkg")
    async def _handler(
        *, job, session, scheduled_for, now
    ):  # pragma: no cover - executed via executor
        return {"job": job.pkg_uid, "run": scheduled_for.isoformat()}

    job_ids: list[str] = []
    for idx in range(3):
        pkg_uid = "limited.pkg" if idx == 0 else f"limited.pkg.{idx}"
        payload = {
            "pkg_uid": pkg_uid,
            "cron_expression": "* * * * *",
            "valid_from": (now - dt.timedelta(minutes=5)).isoformat(),
            "valid_to": (now + dt.timedelta(minutes=5)).isoformat(),
        }
        created = await cron_client.post("/cron/cronjob", json=payload)
        created.raise_for_status()
        job_ids.append(created.json()["id"])

    results = await execute_due_jobs(cron_app, now=now, limit=1)
    assert len(results) == 1

    statuses = []
    for job_id in job_ids:
        stored = await cron_client.get(f"/cron/cronjob/{job_id}")
        stored.raise_for_status()
        statuses.append(stored.json()["last_status"])

    assert statuses.count("success") == 1
