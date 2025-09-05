import pytest
from git import Repo

from peagen.core import init_core


@pytest.mark.unit
def test_configure_repo_adds_remotes(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    remotes = {
        "origin": "https://example.com/origin.git",
        "shadow": "https://git.peagen.com/shadow.git",
    }
    result = init_core.configure_repo(path=repo_dir, remotes=remotes)
    repo = Repo(str(repo_dir))
    configured = {r.name: list(r.urls)[0] for r in repo.remotes}
    assert configured == remotes
    assert result == {"configured": str(repo_dir), "remotes": remotes}
