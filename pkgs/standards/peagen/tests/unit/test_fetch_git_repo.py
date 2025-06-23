from pathlib import Path

from peagen.core.fetch_core import fetch_single
from peagen.plugins.vcs import GitVCS


def test_fetch_single_from_repo(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    vcs = GitVCS.ensure_repo(repo_dir)
    (repo_dir / "file.txt").write_text("data", encoding="utf-8")
    commit_sha = vcs.commit(["file.txt"], "init")
    vcs.create_branch("refs/pea/testbranch", checkout=True)
    (repo_dir / "branch.txt").write_text("b", encoding="utf-8")
    vcs.commit(["branch.txt"], "branch commit")
    vcs.checkout("master")
    out_branch = tmp_path / "out_branch"
    fetch_single(repo=str(repo_dir), ref="refs/heads/master", dest_root=out_branch)
    assert (out_branch / "file.txt").read_text() == "data"

    out_custom = tmp_path / "out_custom"
    fetch_single(repo=str(repo_dir), ref="refs/pea/testbranch", dest_root=out_custom)
    assert (out_custom / "file.txt").read_text() == "data"

    out_commit = tmp_path / "out_commit"
    fetch_single(repo=str(repo_dir), ref=commit_sha, dest_root=out_commit)
    assert (out_commit / "file.txt").read_text() == "data"


def test_fetch_single_detects_updates(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    vcs = GitVCS.ensure_repo(repo_dir)
    (repo_dir / "file.txt").write_text("a", encoding="utf-8")
    vcs.commit(["file.txt"], "init")

    out_dir = tmp_path / "out"
    result = fetch_single(repo=str(repo_dir), ref="HEAD", dest_root=out_dir)
    first_commit = result["commit"]

    (repo_dir / "file.txt").write_text("b", encoding="utf-8")
    vcs.commit(["file.txt"], "update")
    result = fetch_single(repo=str(repo_dir), ref="HEAD", dest_root=out_dir)

    assert result["updated"] is True
    assert result["commit"] != first_commit
