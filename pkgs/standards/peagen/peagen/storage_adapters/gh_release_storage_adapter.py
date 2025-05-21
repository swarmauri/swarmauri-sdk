"""Storage adapter backed by GitHub Releases."""

from __future__ import annotations
from pydantic import SecretStr
import io
import tempfile
from typing import BinaryIO, Optional
from github import Github, UnknownObjectException


class GithubReleaseStorageAdapter:
    """
    Storage adapter that uses GitHub Releases to store and retrieve binary assets.

    - `upload(key, data)`: uploads a file-like object as a release asset named `key`.
      If the asset exists, it will be deleted and replaced.
    - `download(key)`: retrieves the asset named `key` from the release and returns a BytesIO.

    Requires a GitHub personal access token with `repo` scope.
    """

    def __init__(
        self,
        token: SecretStr,
        org: str,
        repo: str,
        tag: str,
        *,
        release_name: Optional[str] = None,
        message: str = "",
        draft: bool = False,
        prerelease: bool = False,
    ):
        self._client = Github(token.get_secret_value())
        self._repo = self._client.get_organization(org).get_repo(repo)
        self._tag = tag
        self._release = self._get_or_create_release(
            tag=tag,
            name=release_name or tag,
            message=message,
            draft=draft,
            prerelease=prerelease,
        )

    @property
    def root_uri(self) -> str:
        """
        Treat a GitHub Release as a ‘bucket’.  Evaluators that understand
        the ghrel:// scheme can fetch assets back.
        Example:  ghrel://my-org/my-repo/v1.3.0/
        """
        return f"ghrel://{self._repo.full_name}/{self._tag}/"

    def _get_or_create_release(
        self,
        tag: str,
        name: str,
        message: str,
        draft: bool,
        prerelease: bool,
    ):
        try:
            return self._repo.get_release(tag)
        except UnknownObjectException:
            return self._repo.create_git_release(
                tag=tag,
                name=name,
                message=message,
                draft=draft,
                prerelease=prerelease,
            )

    def upload(self, key: str, data: BinaryIO) -> None:
        """
        Uploads `data` to the GitHub Release as an asset named `key`.
        If an asset with the same name exists, it's deleted first.
        """
        # Read bytes from data
        data.seek(0)
        content = data.read()

        # Delete existing asset if present
        for asset in self._release.get_assets():
            if asset.name == key:
                asset.delete_asset()
                break

        # Write to a temporary file and upload
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content)
            tmp.flush()
            # upload_asset(path, label=None, name=None)
            self._release.upload_asset(
                path=tmp.name,
                name=key,
                label=key,
            )

    def download(self, key: str) -> BinaryIO:
        """
        Downloads the release asset named `key` and returns it as a BytesIO.
        """
        # Find the asset
        for asset in self._release.get_assets():
            if asset.name == key:
                # Fetch raw bytes via PyGithub's requester
                # _Github__requester.requestBytes returns (status, data_bytes)
                _, raw = self._client._Github__requester.requestBytes(
                    "GET", asset.url,
                    headers={"Accept": "application/octet-stream"},
                )
                buffer = io.BytesIO(raw)
                buffer.seek(0)
                return buffer
        raise FileNotFoundError(f"Asset '{key}' not found in release '{self._tag}'")
