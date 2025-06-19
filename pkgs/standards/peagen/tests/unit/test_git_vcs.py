from pathlib import Path
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

