import pytest
from pathlib import Path
import tempfile
from contextlib import contextmanager
from peagen.plugins.vcs.git_vcs import GitVCS

from peagen.handlers import doe_handler as handler
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
@pytest.mark.asyncio
async def test_doe_handler_calls_generate_payload(monkeypatch):
    captured = {}

    def fake_generate_payload(**kwargs):
        captured.update(kwargs)
        return {"done": True, "dry_run": True}

    monkeypatch.setattr(handler, "generate_payload", fake_generate_payload)

    class DummyPM:
        def __init__(self, cfg):
            self.cfg = cfg

        def get(self, name):
            raise Exception

    monkeypatch.setattr(handler, "PluginManager", DummyPM)

    @contextmanager
    def dummy_lock(_repo: str):
        yield

    def fake_open_repo(path, remote_url=None):
        tmp = Path(tempfile.mkdtemp())
        return GitVCS(tmp)

    monkeypatch.setattr(handler, "repo_lock", dummy_lock)
    monkeypatch.setattr(handler, "open_repo", fake_open_repo)
    monkeypatch.setattr(handler, "fetch_git_remote", lambda *_: None)
    monkeypatch.setattr(handler, "add_git_worktree", lambda *_: None)

    async def fake_fan_out(**_):
        return {"children": [], "jobs": 0}

    monkeypatch.setattr(handler, "fan_out", fake_fan_out)

    class DummyStatus:
        waiting = object()

    monkeypatch.setattr(handler, "Status", DummyStatus)

    args = {
        "spec": "spec.yml",
        "template": "templ.j2",
        "output": "out.json",
        "config": "cfg.toml",
        "notify": "http://x",
        "dry_run": True,
        "force": True,
        "skip_validate": True,
        "repo": "repo",
        "ref": "HEAD",
    }

    task = build_task(
        action="doe",
        args=args,
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    result = await handler.doe_handler(task)

    assert result == {"done": True, "dry_run": True, "children": [], "jobs": 0}
    assert captured["spec_path"].name == "spec.yml"
    assert captured["dry_run"] is True
