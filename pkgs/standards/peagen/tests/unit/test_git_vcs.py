from pathlib import Path

import json

import pytest

from peagen.plugins.vcs import GitVCS, pea_ref
from peagen.errors import GitRemoteMissingError
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
