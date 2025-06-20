import yaml
from pathlib import Path
from peagen.plugins.vcs import GitVCS, pea_ref
from peagen.core.doe_core import (
    create_factor_branches,
    create_run_branches,
)


import pytest


@pytest.mark.unit
def test_factor_and_run_branches(tmp_path: Path, monkeypatch) -> None:
    repo_dir = tmp_path / "repo"
    vcs = GitVCS.ensure_repo(repo_dir)

    def safe_switch(branch: str) -> None:
        vcs.repo.git.checkout(branch)

    monkeypatch.setattr(vcs, "switch", safe_switch)

    def run_branches_allow_empty(vcs_obj, points, *_args, **_kwargs):
        branches = []
        for point in points:
            label = "_".join(f"{k}-{v}" for k, v in point.items())
            branch = pea_ref("run", label)
            vcs_obj.create_branch(branch, "HEAD")
            vcs_obj.switch(branch)
            parents = [pea_ref("factor", k, v) for k, v in point.items()]
            if parents:
                vcs_obj.repo.git.merge("--no-ff", "--no-edit", *parents)
            vcs_obj.repo.git.commit("--allow-empty", "-m", f"run {label}")
            branches.append(branch)
        vcs_obj.switch("HEAD")
        return branches

    base = repo_dir / "base.yaml"
    base.write_text("a: 1\n", encoding="utf-8")
    vcs.commit(["base.yaml"], "base")

    spec = {
        "version": "v2",
        "meta": {"name": "t"},
        "baseArtifact": "base.yaml",
        "factors": [
            {
                "name": "opt",
                "levels": [
                    {
                        "id": "adam",
                        "patchRef": "p1.yaml",
                        "output_path": "artifact.yaml",
                        "patchKind": "json-merge",
                    }
                ],
            },
            {
                "name": "lr",
                "levels": [
                    {
                        "id": "small",
                        "patchRef": "p2.yaml",
                        "output_path": "artifact.yaml",
                        "patchKind": "json-merge",
                    }
                ],
            },
        ],
    }

    (repo_dir / "p1.yaml").write_text("b: 2\n", encoding="utf-8")
    (repo_dir / "p2.yaml").write_text("c: 3\n", encoding="utf-8")
    vcs.repo.git.add(["p1.yaml", "p2.yaml"])
    vcs.repo.git.commit("-m", "patch files")

    create_factor_branches(vcs, spec, repo_dir)
    vcs.checkout(pea_ref("factor", "opt", "adam"))
    data = yaml.safe_load((repo_dir / "artifact.yaml").read_text())
    assert data["b"] == 2

    create_run_branches(vcs, spec, repo_dir)
    vcs.checkout(pea_ref("run", "opt-adam_lr-small"))
    data = yaml.safe_load((repo_dir / "artifact.yaml").read_text())
    assert data["b"] == 2 and data["c"] == 3
