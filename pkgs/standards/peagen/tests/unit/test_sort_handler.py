import pytest

from peagen.handlers import sort_handler as handler
from peagen.cli.task_helpers import build_task
from peagen.orm import Action
from uuid import uuid4


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

    task = build_task(
        action=Action.SORT,
        args=args,
        tenant_id=str(uuid4()),
        pool_id=str(uuid4()),
        repo="repo",
        ref="HEAD",
    )
    result = await handler.sort_handler(task)

    if project_name:
        assert "single" in calls
        assert result == {"single": True}
    else:
        assert "all" in calls
        assert result == {"all": True}
