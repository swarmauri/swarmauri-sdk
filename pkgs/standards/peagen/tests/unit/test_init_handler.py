import pytest
from pathlib import Path

from peagen.handlers import init_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone
from peagen.core import init_core


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind, func",
    [
        ("project", "init_project"),
        ("template-set", "init_template_set"),
        ("doe-spec", "init_doe_spec"),
        ("ci", "init_ci"),
    ],
)
async def test_init_handler_dispatch(monkeypatch, kind, func):
    called = {}

    def fake(**kwargs):
        called.update(kwargs)
        return {"kind": kind}

    monkeypatch.setattr(init_core, func, fake)
    args = {"kind": kind, "path": "~/p"}
    task = TaskRead.model_construct(
        id=str(uuid.uuid4()),
        tenant_id=uuid.uuid4(),
        git_reference_id=None,
        pool="default",
        payload={"args": args},
        status=Status.queued,
        note=None,
        spec_hash="",
        date_created=datetime.now(timezone.utc),
        last_modified=datetime.now(timezone.utc),
    )
    result = await handler.init_handler(task)

    assert result == {"kind": kind}
    assert called.get("path") == Path("~/p").expanduser()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_init_handler_errors(monkeypatch):
    with pytest.raises(ValueError):
        task = TaskRead.model_construct(
            id=str(uuid.uuid4()),
            tenant_id=uuid.uuid4(),
            git_reference_id=None,
            pool="default",
            payload={"args": {}},
            status=Status.queued,
            note=None,
            spec_hash="",
            date_created=datetime.now(timezone.utc),
            last_modified=datetime.now(timezone.utc),
        )
        await handler.init_handler(task)

    with pytest.raises(ValueError):
        task = TaskRead.model_construct(
            id=str(uuid.uuid4()),
            tenant_id=uuid.uuid4(),
            git_reference_id=None,
            pool="default",
            payload={"args": {"kind": "unknown"}},
            status=Status.queued,
            note=None,
            spec_hash="",
            date_created=datetime.now(timezone.utc),
            last_modified=datetime.now(timezone.utc),
        )
        await handler.init_handler(task)
