from pathlib import Path

import json

import pytest

from peagen.plugins.vcs import GitVCS, pea_ref
from peagen.errors import (
    GitRemoteMissingError,
    GitCloneError,
    GitFetchError,
    GitCommitError,
)
from peagen.plugins.secret_drivers import SecretDriverBase


def test_gitvcs_promote(tmp_path: Path):
    repo_dir = tmp_path / "r"
    vcs = GitVCS.ensure_repo(repo_dir)
    (repo_dir / "file.txt").write_text("data")
    vcs.commit(["file.txt"], "init")
    run_ref = pea_ref("run", "a")
    vcs.tag(run_ref)
    vcs.promote(run_ref, "promoted/a")
    assert "promoted/a" in [h.name for h in vcs.repo.heads]


def test_gitvcs_fan_out(tmp_path: Path):
    repo_dir = tmp_path / "fanout"
    vcs = GitVCS.ensure_repo(repo_dir)
    (repo_dir / "base.txt").write_text("base")
    vcs.commit(["base.txt"], "init")

    b1 = pea_ref("factor", "a")
    b2 = pea_ref("factor", "b")
    vcs.fan_out("HEAD", [b1, b2])

    branches = {h.name for h in vcs.repo.heads}
    assert {b1, b2} <= branches


def test_gitvcs_merge_ours(tmp_path: Path):
    repo_dir = tmp_path / "ours"
    vcs = GitVCS.ensure_repo(repo_dir)
    (repo_dir / "base.txt").write_text("base")
    vcs.commit(["base.txt"], "base")

    vcs.create_branch("run/x", checkout=True)
    (repo_dir / "child.txt").write_text("child")
    vcs.commit(["child.txt"], "child")

    vcs.switch("master")
    vcs.merge_ours("run/x", "ours merge")
    commit = vcs.repo.head.commit
    assert commit.message.strip() == "ours merge"
    assert not (repo_dir / "child.txt").exists()


def test_fast_import_json_ref(tmp_path: Path):
    repo_dir = tmp_path / "audit"
    vcs = GitVCS.ensure_repo(repo_dir)
    ref = pea_ref("key_audit", "abc")
    payload = {"user_fpr": "A", "gateway_fp": "B"}
    sha = vcs.fast_import_json_ref(ref, payload)
    stored = vcs.repo.git.show(f"{sha}:audit.json")
    assert json.loads(stored) == payload


def test_record_key_audit(tmp_path: Path):
    repo_dir = tmp_path / "ka"
    vcs = GitVCS.ensure_repo(repo_dir)
    secret = b"topsecret"
    sha = vcs.record_key_audit(secret, "UFPR", "GFPR")
    stored = vcs.repo.git.show(f"{sha}:audit.json")
    data = json.loads(stored)
    assert data["user_fpr"] == "UFPR"
    assert data["gateway_fp"] == "GFPR"
    ref = pea_ref("key_audit", SecretDriverBase.audit_hash(secret))
    assert vcs.repo.rev_parse(ref) == sha


def test_push_no_remote(tmp_path: Path) -> None:
    repo_dir = tmp_path / "noremote"
    vcs = GitVCS.ensure_repo(repo_dir)
    (repo_dir / "file.txt").write_text("x")
    vcs.commit(["file.txt"], "init")
    with pytest.raises(GitRemoteMissingError):
        vcs.push("HEAD")


def test_clone_error(tmp_path: Path) -> None:
    bad_remote = tmp_path / "no_repo"
    with pytest.raises(GitCloneError):
        GitVCS.ensure_repo(tmp_path / "clone", remote_url=str(bad_remote))


def test_fetch_error(tmp_path: Path) -> None:
    repo_src = tmp_path / "src"
    vcs_src = GitVCS.ensure_repo(repo_src)
    (repo_src / "file.txt").write_text("x")
    vcs_src.commit(["file.txt"], "init")

    repo_clone = tmp_path / "clone"
    vcs_clone = GitVCS.ensure_repo(repo_clone, remote_url=str(repo_src))
    with pytest.raises(GitFetchError):
        vcs_clone.fetch("refs/heads/missing")


def test_commit_error_outside_repo(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    vcs = GitVCS.ensure_repo(repo_dir)
    (repo_dir / "file.txt").write_text("x")
    vcs.commit(["file.txt"], "init")

    outside = tmp_path / "outside.txt"
    outside.write_text("oops")
    with pytest.raises(GitCommitError):
        vcs.commit([str(outside)], "fail")


def test_remote_helpers(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    vcs = GitVCS.ensure_repo(repo_dir)

    assert not vcs.has_remote()
    with pytest.raises(GitRemoteMissingError):
        vcs.require_remote()

    vcs.configure_remote("https://example.com/repo.git")
    assert vcs.has_remote()
    vcs.require_remote()
    assert vcs.repo.remotes.origin.url == "https://example.com/repo.git"

    # updating the remote should change the url
    vcs.configure_remote("https://example.com/new.git")
    assert vcs.repo.remotes.origin.url == "https://example.com/new.git"


def test_mirror_push(tmp_path: Path) -> None:
    origin = tmp_path / "origin"
    mirror = tmp_path / "mirror"
    clone = tmp_path / "clone"

    vcs_origin = GitVCS.ensure_repo(origin)
    (origin / "base.txt").write_text("base")
    vcs_origin.commit(["base.txt"], "init")

    GitVCS.ensure_repo(mirror)

    vcs = GitVCS.ensure_repo(
        clone,
        remote_url=str(origin),
        mirror_git_url=str(mirror),
    )
    vcs.fetch("HEAD")
    (clone / "new.txt").write_text("new")
    vcs.commit(["new.txt"], "update")
    vcs.push("HEAD")

    assert (mirror / "new.txt").exists()
