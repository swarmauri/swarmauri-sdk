"""Test helpers for swarmauri_gitfilter_gh_release."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


class DummyAsset:
    """Mimic a GitHub release asset for tests."""

    def __init__(self, name: str, data: bytes) -> None:
        self.name = name
        self.url = name
        self._data = data

    def delete_asset(self) -> None:
        """Match the PyGithub API."""

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"DummyAsset(name={self.name!r})"


class DummyRelease:
    """Hold uploaded assets in-memory."""

    def __init__(self) -> None:
        self.assets: list[DummyAsset] = []

    def get_assets(self) -> Iterable[DummyAsset]:
        return list(self.assets)

    def upload_asset(self, path: str | Path, name: str, label: str) -> None:
        with Path(path).open("rb") as fh:
            self.assets.append(DummyAsset(name, fh.read()))


class DummyRepo:
    """Subset of Repo API used by GithubReleaseFilter."""

    def __init__(self, release: DummyRelease) -> None:
        self.full_name = "org/repo"
        self._release = release

    def get_release(self, tag: str) -> DummyRelease:
        return self._release

    def create_git_release(self, **_kwargs) -> DummyRelease:
        return self._release


class DummyOrg:
    def __init__(self, release: DummyRelease) -> None:
        self._release = release

    def get_repo(self, _repo: str) -> DummyRepo:
        return DummyRepo(self._release)


class DummyRequester:
    def __init__(self, release: DummyRelease) -> None:
        self._release = release

    def requestBytes(self, _method: str, url: str, headers: dict | None = None):  # noqa: N802 - PyGithub API
        asset = next(asset for asset in self._release.get_assets() if asset.url == url)
        return None, asset._data


def patch_dummy_github(monkeypatch) -> DummyRelease:
    """Patch PyGithub's ``Github`` class with an in-memory fake."""

    release = DummyRelease()

    class DummyGithub:
        def __init__(self, _token: str) -> None:
            self._release = release
            self._Github__requester = DummyRequester(self._release)

        def get_organization(self, _org: str):
            return DummyOrg(self._release)

    monkeypatch.setattr(
        "swarmauri_gitfilter_gh_release.gh_release_filter.Github", DummyGithub
    )
    return release
