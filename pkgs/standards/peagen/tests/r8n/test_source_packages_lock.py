import json
import subprocess
from pathlib import Path

import pytest
import typer

from peagen._source_packages import materialise_packages


def _init_git_repo(repo: Path) -> str:
    repo.mkdir()
    subprocess.check_call(["git", "init"], cwd=repo)
    subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=repo)
    subprocess.check_call(["git", "config", "user.name", "Tester"], cwd=repo)
    (repo / "file.txt").write_text("hello", encoding="utf-8")
    subprocess.check_call(["git", "add", "file.txt"], cwd=repo)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=repo)
    sha = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo).decode().strip()
    )
    return sha


@pytest.mark.r8n
def test_materialise_packages_lock(tmp_path: Path):
    repo = tmp_path / "repo"
    sha1 = _init_git_repo(repo)

    workspace = tmp_path / "ws"
    workspace.mkdir()

    packages = [{"type": "git", "uri": str(repo), "dest": "src"}]

    materialise_packages(packages, workspace)

    lock_file = workspace / "source_packages.lock"
    assert lock_file.exists()
    data = json.loads(lock_file.read_text())
    assert data["src"] == sha1
    assert packages[0]["checksum"] == sha1

    # create new commit
    (repo / "file.txt").write_text("update", encoding="utf-8")
    subprocess.check_call(["git", "add", "file.txt"], cwd=repo)
    subprocess.check_call(["git", "commit", "-m", "update"], cwd=repo)

    with pytest.raises(typer.Exit):
        materialise_packages(packages, workspace)
