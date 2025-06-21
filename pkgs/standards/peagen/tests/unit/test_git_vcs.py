from pathlib import Path

import json

from peagen.plugins.vcs import GitVCS, pea_ref


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
