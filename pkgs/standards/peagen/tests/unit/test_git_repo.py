from pathlib import Path

import pytest

from peagen.git.repo import get_repo


@pytest.mark.unit
def test_get_repo_initializes(tmp_path: Path):
    repo = get_repo(tmp_path)
    assert (tmp_path / ".git").is_dir()
    assert repo.working_tree_dir == str(tmp_path)


@pytest.mark.unit
def test_get_repo_reuses_existing(tmp_path: Path):
    first = get_repo(tmp_path)
    second = get_repo(tmp_path)
    assert first.git_dir == second.git_dir
