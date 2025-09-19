from swarmauri_gitfilter_gh_release import GithubReleaseFilter

from .._helpers import patch_dummy_github


def create_filter(monkeypatch):
    patch_dummy_github(monkeypatch)
    return GithubReleaseFilter.from_uri("ghrel://org/repo/tag")


def test_resource_type_serialization(monkeypatch):
    filt = create_filter(monkeypatch)
    assert filt.resource == "StorageAdapter"
    assert filt.type == "GithubReleaseFilter"
    data = filt.model_dump()
    restored = GithubReleaseFilter(token="", org="org", repo="repo", tag="tag", **data)
    assert restored.type == filt.type


def test_clean_smudge(monkeypatch):
    filt = create_filter(monkeypatch)
    oid = filt.clean(b"hello")
    assert filt.smudge(oid) == b"hello"
