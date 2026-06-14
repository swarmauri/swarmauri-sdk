import pytest

from swarmauri_gitfilter_gh_release import GithubReleaseFilter

from .._helpers import DummyAsset, patch_dummy_github


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


def test_download_prefix_rejects_path_traversal_asset(monkeypatch, tmp_path):
    release = patch_dummy_github(monkeypatch)
    release.assets.append(DummyAsset("safe/../escaped.txt", b"owned"))
    filt = GithubReleaseFilter.from_uri("ghrel://org/repo/tag")
    dest = tmp_path / "dest"
    outside = tmp_path / "escaped.txt"

    with pytest.raises(ValueError, match="unsafe storage key"):
        filt.download_prefix("safe", dest)

    assert not outside.exists()
