import pytest

from peagen.handlers import mutate_handler as handler
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mutate_handler_invokes_core(monkeypatch):
    captured = {}

    def fake_mutate_workspace(**kwargs):
        captured.update(kwargs)
        return {"winner": "w.py", "score": "1", "meta": {"ok": True}}

    monkeypatch.setattr(handler, "mutate_workspace", fake_mutate_workspace)

    class DummyPM:
        def __init__(self, cfg):
            self.cfg = cfg

        def get(self, name):
            raise Exception

    monkeypatch.setattr(handler, "PluginManager", DummyPM)

    args = {
        "repo": "repo",
        "ref": "HEAD",
        "target_file": "t.py",
        "import_path": "mod",
        "entry_fn": "f",
        "gens": 3,
        "profile_mod": None,
        "config": "conf.toml",
        "mutations": [{"kind": "echo_mutator", "probability": 1}],
        "evaluator": "ev",
    }

    task = build_task(
        action="mutate",
        args=args,
        pool_id="default",
        repo="repo",
        ref="HEAD",
    )

    result = await handler.mutate_handler(task)

    assert result == {"winner": "w.py", "score": "1", "meta": {"ok": True}}
    assert captured["repo"] == "repo"
    assert captured["ref"] == "HEAD"
    assert captured["target_file"] == "t.py"
    assert captured["import_path"] == "mod"
    assert captured["entry_fn"] == "f"
    assert captured["gens"] == 3
    assert captured["mutations"] == [{"kind": "echo_mutator", "probability": 1}]
    assert captured["evaluator_ref"] == "ev"
