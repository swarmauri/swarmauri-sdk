import io


from swarmauri_storage_github_release import GithubReleaseStorageAdapter


class DummyAsset:
    def __init__(self, name, data):
        self.name = name
        self.url = name
        self._data = data

    def delete_asset(self):
        pass


class DummyRelease:
    def __init__(self):
        self.assets: list[DummyAsset] = []

    def get_assets(self):
        return self.assets

    def upload_asset(self, path, name, label):
        with open(path, "rb") as fh:
            self.assets.append(DummyAsset(name, fh.read()))


class DummyRepo:
    def __init__(self, release):
        self.full_name = "org/repo"
        self._release = release

    def get_release(self, tag):
        return self._release

    def create_git_release(self, **kwargs):
        return self._release


class DummyOrg:
    def __init__(self, release):
        self._release = release

    def get_repo(self, repo):
        return DummyRepo(self._release)


class DummyRequester:
    def __init__(self, release):
        self._release = release

    def requestBytes(self, method, url, headers=None):
        asset = next(a for a in self._release.get_assets() if a.url == url)
        return None, asset._data


class DummyGithub:
    def __init__(self, token):
        self._release = DummyRelease()
        self._Github__requester = DummyRequester(self._release)

    def get_organization(self, org):
        return DummyOrg(self._release)


def create_adapter(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_storage_github_release.gh_release_storage_adapter.Github",
        DummyGithub,
    )
    return GithubReleaseStorageAdapter.from_uri("ghrel://org/repo/tag")


def test_resource_type_serialization(monkeypatch):
    adapter = create_adapter(monkeypatch)
    assert adapter.resource == "StorageAdapter"
    assert adapter.type == "GithubReleaseStorageAdapter"
    data = adapter.model_dump()
    restored = GithubReleaseStorageAdapter(
        token="", org="org", repo="repo", tag="tag", **data
    )
    assert restored.type == adapter.type


def test_upload_download(monkeypatch):
    adapter = create_adapter(monkeypatch)
    uri = adapter.upload("foo.txt", io.BytesIO(b"hi"))
    assert uri.endswith("foo.txt")
    data = adapter.download("foo.txt").read()
    assert data == b"hi"
