import pytest
from pathlib import Path
from peagen.core.mirror_core import ensure_repo
from peagen.handlers import mutate_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mutate_handler_repo(tmp_path: Path, monkeypatch):
    repo_dir = tmp_path / "repo"
    vcs = ensure_repo(repo_dir)
    (repo_dir / "t.py").write_text("x = 1", encoding="utf-8")
    vcs.commit(["t.py"], "init")

    # Prevent push errors for the local repo without a remote
    from peagen.plugins.vcs import GitVCS

    monkeypatch.setattr(GitVCS, "push", lambda self, branch: None)

    captured = {}

    def fake_mutate_workspace(**kwargs):
        captured.update(kwargs)
        return {
            "winner": str(Path(kwargs["workspace_uri"]) / "winner.py"),
            "score": "0",
            "meta": {"ok": True},
        }

    monkeypatch.setattr(handler, "mutate_workspace", fake_mutate_workspace)

    args = {
        "repo": str(repo_dir),
        "ref": "HEAD",
        "workspace_uri": "unused",
        "target_file": "t.py",
        "import_path": "mod",
        "entry_fn": "bench",
        "gens": 1,
        "evaluator_ref": "ev",
    }

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
    result = await handler.mutate_handler(task)

    assert not Path(captured["workspace_uri"]).exists()
    assert result["score"] == "0"
    assert result["meta"] == {"ok": True}
    assert result["commit"] is None
    assert "winner_oid" not in result
