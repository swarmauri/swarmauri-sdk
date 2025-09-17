"""Ensure README examples remain executable."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import Dict

import pytest

from swarmauri_storage_github_release import (
    gh_release_storage_adapter as adapter_module,
)


@pytest.mark.example
def test_usage_example_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute the primary README example to guard against regressions."""

    readme_path = Path(__file__).resolve().parents[2] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    match = re.search(r"```python\n(.*?)\n```", readme_text, flags=re.DOTALL)
    assert match, "Unable to locate python example in README.md"

    example_code = textwrap.dedent(match.group(1))

    class DummyUnknownObjectException(Exception):
        """Replacement for PyGithub's UnknownObjectException."""

    monkeypatch.setattr(
        adapter_module,
        "UnknownObjectException",
        DummyUnknownObjectException,
    )

    class DummyRequester:
        """Minimal requester that serves uploaded asset payloads."""

        def __init__(self) -> None:
            self.asset_payloads: Dict[str, bytes] = {}

        def requestBytes(self, method: str, url: str, headers: Dict[str, str]):  # noqa: N802 - PyGithub naming
            return None, self.asset_payloads[url]

    requester = DummyRequester()

    class DummyAsset:
        """Simple asset representation that cooperates with the adapter."""

        def __init__(self, release: DummyRelease, name: str, data: bytes) -> None:  # type: ignore[name-defined]
            self._release = release
            self.name = name
            self.url = f"https://example.invalid/{release.repo.full_name}/{name}"
            requester.asset_payloads[self.url] = data

        def delete_asset(self) -> None:
            self._release.remove_asset(self.name)

    class DummyRelease:
        """Release facade storing uploaded assets in-memory."""

        def __init__(
            self, client: DummyGithub, repo: DummyRepo, tag: str, name: str
        ) -> None:  # type: ignore[name-defined] # noqa: PLR0913
            self._client = client
            self.repo = repo
            self.tag = tag
            self.name = name
            self._assets: Dict[str, DummyAsset] = {}

        def get_assets(self):
            return list(self._assets.values())

        def upload_asset(self, path: str, name: str, label: str) -> None:  # noqa: ARG002 - label unused in stub
            data = Path(path).read_bytes()
            self._assets[name] = DummyAsset(self, name, data)

        def remove_asset(self, name: str) -> None:
            asset = self._assets.pop(name, None)
            if asset:
                requester.asset_payloads.pop(asset.url, None)

    class DummyRepo:
        """Repository wrapper that can create and fetch releases."""

        def __init__(self, client: DummyGithub, full_name: str) -> None:  # type: ignore[name-defined]
            self._client = client
            self.full_name = full_name
            self._releases: Dict[str, DummyRelease] = {}

        def get_release(self, tag: str) -> DummyRelease:
            if tag not in self._releases:
                raise adapter_module.UnknownObjectException(tag)
            return self._releases[tag]

        def create_git_release(
            self,
            tag: str,
            name: str,
            message: str,
            draft: bool,
            prerelease: bool,
        ) -> DummyRelease:  # noqa: ARG002
            release = DummyRelease(self._client, self, tag, name)
            self._releases[tag] = release
            return release

    class DummyOrg:
        """Organization shim returning deterministic repositories."""

        def __init__(self, client: DummyGithub, name: str) -> None:  # type: ignore[name-defined]
            self._client = client
            self._name = name
            self._repos: Dict[str, DummyRepo] = {}

        def get_repo(self, repo_name: str) -> DummyRepo:
            return self._repos.setdefault(
                repo_name,
                DummyRepo(self._client, f"{self._name}/{repo_name}"),
            )

    class DummyGithub:
        """Drop-in replacement for ``PyGithub.Github`` used in the example."""

        def __init__(self, token: str) -> None:
            self.token = token
            self._Github__requester = requester
            self._orgs: Dict[str, DummyOrg] = {}

        def get_organization(self, name: str) -> DummyOrg:
            return self._orgs.setdefault(name, DummyOrg(self, name))

    monkeypatch.setattr(adapter_module, "Github", DummyGithub)

    namespace: Dict[str, object] = {}
    exec(compile(example_code, str(readme_path), "exec"), namespace)

    assert namespace["uri"] == (
        "ghrel://example-org/example-repo/v1.0.0/artifacts/artifacts/artifact.txt"
    )
    assert namespace["downloaded_payload"] == b"important payload"
    assert namespace["assets"] == ["artifact.txt"]
