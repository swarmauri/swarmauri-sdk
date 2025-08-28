from swarmauri_base import GitFilterBase
from swarmauri_gitfilter_github_release import GithubReleaseFilter


def test_inherits_base():
    assert issubclass(GithubReleaseFilter, GitFilterBase)
