import pytest
from git import Repo
from unittest.mock import Mock, call, patch

from peagen.core import init_core


@pytest.mark.unit
@patch("peagen.core.init_core.open_repo")
@patch("peagen.core.init_core.configure_repo")
@patch("peagen.core.init_core.Github")
def test_init_repo_configures_and_pushes(
    GithubMock, configure_repo_mock, open_repo_mock, tmp_path
):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    repo = Repo.init(repo_dir)
    (repo_dir / "README.md").write_text("hi")
    repo.git.add(all=True)
    repo.git.config("user.email", "test@example.com")
    repo.git.config("user.name", "Test User")
    repo.git.commit("-m", "init")

    gh = GithubMock.return_value
    owner = Mock()
    gh.get_organization.side_effect = Exception
    gh.get_user.return_value = owner
    repo_obj = Mock()
    repo_obj.clone_url = "https://github.com/principal/repo.git"
    repo_obj.ssh_url = "git@github.com:principal/repo.git"
    owner.create_repo.return_value = repo_obj
    repo_obj.create_key.return_value = None

    vcs_mock = Mock()
    open_repo_mock.return_value = vcs_mock

    result = init_core.init_repo(repo="principal/repo", pat="TOKEN", path=repo_dir)

    expected_remotes = {
        "origin": "https://git.peagen.com/principal/repo.git",
        "upstream": "git@github.com:principal/repo.git",
    }
    configure_repo_mock.assert_called_once_with(path=repo_dir, remotes=expected_remotes)
    open_repo_mock.assert_called_once_with(repo_dir, remotes=expected_remotes)
    assert vcs_mock.push.call_args_list == [
        call("HEAD", remote="origin"),
        call("HEAD", remote="upstream"),
    ]
    assert result["remotes"] == expected_remotes
