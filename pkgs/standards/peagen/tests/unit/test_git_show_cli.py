import json
import subprocess
from git import Repo
import pytest


@pytest.mark.unit
def test_git_show_inspects_commit_tree_blob(tmp_path):
    repo = Repo.init(tmp_path)
    (tmp_path / "file.txt").write_text("hello", encoding="utf-8")
    repo.index.add(["file.txt"])
    repo.index.commit("init commit")

    commit_oid = repo.head.commit.hexsha
    tree_oid = repo.head.commit.tree.hexsha
    blob_oid = repo.head.commit.tree["file.txt"].hexsha

    def run_show(oid: str):
        result = subprocess.run(
            [
                "peagen",
                "local",
                "-q",
                "git",
                "show",
                oid,
                "--repo",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.strip().splitlines()
        start = next(i for i, line in enumerate(lines) if line.strip().startswith("{"))
        return json.loads("\n".join(lines[start:]))

    commit_info = run_show(commit_oid)
    assert commit_info["type"] == "commit"
    assert "init commit" in commit_info["pretty"]
    assert commit_info["size"] > 0

    tree_info = run_show(tree_oid)
    assert tree_info["type"] == "tree"
    assert "file.txt" in tree_info["pretty"]
    assert tree_info["size"] > 0

    blob_info = run_show(blob_oid)
    assert blob_info["type"] == "blob"
    assert blob_info["pretty"] == "hello"
    assert blob_info["size"] == len("hello")
