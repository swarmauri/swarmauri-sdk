import pytest

from peagen.handlers import sort_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("project_name", ["proj", None])
async def test_sort_handler_delegates(monkeypatch, project_name):
    calls = {}

    def fake_resolve_cfg(toml_text=None):
        return {"cfg": True}

    def fake_single(params):
        calls["single"] = params
        return {"single": True}

    def fake_all(params):
        calls["all"] = params
        return {"all": True}

    monkeypatch.setattr(handler, "resolve_cfg", fake_resolve_cfg)
    monkeypatch.setattr(handler, "sort_single_project", fake_single)
    monkeypatch.setattr(handler, "sort_all_projects", fake_all)

    args = {"projects_payload": "payload"}
    if project_name:
        args["project_name"] = project_name

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
    result = await handler.sort_handler(task)

    if project_name:
        assert "single" in calls
        assert result == {"single": True}
    else:
        assert "all" in calls
        assert result == {"all": True}
