import pytest

from peagen.handlers import process_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


class DummyPM:
    def __init__(self, cfg):
        self.cfg = cfg

    def get(self, name):
        return "adapter"


class DummyAdapter:
    def __init__(self, **kw):
        pass


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("project_name", ["proj", None])
async def test_process_handler_dispatch(monkeypatch, project_name):
    monkeypatch.setattr(handler, "resolve_cfg", lambda toml_text=None: {})
    monkeypatch.setattr(handler, "PluginManager", DummyPM)
    monkeypatch.setattr(handler, "FileStorageAdapter", DummyAdapter)

    calls = {}

    def fake_load(payload):
        calls["load"] = payload
        return [{"NAME": project_name}] if project_name else []

    def fake_single(project, cfg, start_idx, start_file, transitive):
        calls["single"] = project
        return ["done"], 0, "sha", ["oid"]

    def fake_all(payload, cfg, transitive):
        calls["all"] = payload
        return {"all": True}

    monkeypatch.setattr(handler, "load_projects_payload", fake_load)
    monkeypatch.setattr(handler, "process_single_project", fake_single)
    monkeypatch.setattr(handler, "process_all_projects", fake_all)

    args = {"projects_payload": "pp"}
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
    result = await handler.process_handler(task)

    if project_name:
        assert calls["single"] == {"NAME": project_name}
        assert result["processed"] == {project_name: ["done"]}
    else:
        assert calls["all"] == "pp"
        assert result["processed"] == {"all": True}
