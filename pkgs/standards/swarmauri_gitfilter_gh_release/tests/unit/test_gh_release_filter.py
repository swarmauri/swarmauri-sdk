from swarmauri_gitfilter_gh_release import GithubReleaseFilter


class DummyRelease:
    def get_assets(self):
        return []

    def upload_asset(self, *a, **k):
        pass


class DummyRepo:
    def __init__(self):
        self.full_name = "org/repo"

    def get_release(self, tag):
        return DummyRelease()

    def create_git_release(self, *a, **k):
        return DummyRelease()


class DummyOrg:
    def get_repo(self, repo):
        return DummyRepo()


class DummyGithub:
    def __init__(self, *a, **k):
        pass

    def get_organization(self, org):
        return DummyOrg()

    _Github__requester = type(
        "R", (), {"requestBytes": lambda self, *a, **k: (None, b"")}
    )()


def test_from_uri(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_gitfilter_gh_release.gh_release_filter.Github",
        DummyGithub,
    )
    filt = GithubReleaseFilter.from_uri("ghrel://org/repo/tag")
    assert isinstance(filt, GithubReleaseFilter)
