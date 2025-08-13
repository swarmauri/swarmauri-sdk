import pytest

from peagen.handlers import process_handler as handler
from peagen.cli.task_helpers import build_task


class DummyPM:
    def __init__(self, cfg):
        self.cfg = cfg

    def get(self, name):
        raise Exception


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("project_name", ["proj", None])
async def test_process_handler_dispatch(monkeypatch, tmp_path, project_name):
    monkeypatch.setattr(
        handler,
        "resolve_cfg",
        lambda toml_text=None, toml_path=".peagen.toml": {},
    )
    monkeypatch.setattr(handler, "PluginManager", DummyPM)

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

    args = {"projects_payload": "pp", "worktree": str(tmp_path)}
    if project_name:
        args["project_name"] = project_name

    task = build_task(
        action="process",
        args=args,
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )

    result = await handler.process_handler(task)

    if project_name:
        assert calls["single"] == {"NAME": project_name}
        assert result["processed"] == {project_name: ["done"]}
    else:
        assert calls["all"] == "pp"
        assert result["processed"] == {"all": True}
