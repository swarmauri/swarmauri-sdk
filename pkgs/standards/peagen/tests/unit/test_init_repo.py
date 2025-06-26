from pathlib import Path

import pytest

from peagen.core import init_core
from peagen.core.mirror_core import ensure_repo


class DummyRepo:
    def __init__(self):
        self.keys = []

    def create_key(self, title: str, key: str, read_only: bool = False):
        self.keys.append((title, key, read_only))


class DummyOwner:
    def __init__(self):
        self.repo = DummyRepo()

    def create_repo(self, name, private=True, description=""):
        return self.repo


class DummyGH:
    def __init__(self, pat):
        self.owner = DummyOwner()

    def get_organization(self, tenant):
        return self.owner

    def get_user(self, tenant):
        return self.owner

    def get_repo(self, repo):
        return self.owner.repo


@pytest.mark.unit
def test_init_repo_configures_local_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(init_core, "Github", DummyGH)
    repo_dir = tmp_path / "local"
    remotes = {
        "origin": "git@gitea.local:demo/repo.git",
        "upstream": "git@github.com:demo/repo.git",
    }
    result = init_core.init_repo(
        repo="demo/repo",
        pat="dummy",
        path=repo_dir,
        remotes=remotes,
    )
    assert result["configured"] == str(repo_dir)
    for name, url in remotes.items():
        assert url == ensure_repo(repo_dir).repo.remotes[name].url
