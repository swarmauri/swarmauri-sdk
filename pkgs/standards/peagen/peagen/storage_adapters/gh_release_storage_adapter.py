"""Storage adapter backed by GitHub Releases."""

from __future__ import annotations
from pydantic import SecretStr
import io
import os
import shutil
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional

from peagen.cli_common import load_peagen_toml
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
        prefix: str = "",
    ):
        self._client = Github(token.get_secret_value())
        self._repo = self._client.get_organization(org).get_repo(repo)
        self._tag = tag
        self._prefix = prefix.lstrip("/")
        self._release = self._get_or_create_release(
            tag=tag,
            name=release_name or tag,
            message=message,
            draft=draft,
            prerelease=prerelease,
        )

    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    @property
    def root_uri(self) -> str:
        """
        Treat a GitHub Release as a ‘bucket’.  Evaluators that understand
        the ghrel:// scheme can fetch assets back.
        Example:  ghrel://my-org/my-repo/v1.3.0/
        """
        base = f"ghrel://{self._repo.full_name}/{self._tag}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

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
        key = self._full_key(key)

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
        key = self._full_key(key)

        # Find the asset
        for asset in self._release.get_assets():
            if asset.name == key:
                # Fetch raw bytes via PyGithub's requester
                # _Github__requester.requestBytes returns (status, data_bytes)
                _, raw = self._client._Github__requester.requestBytes(
                    "GET",
                    asset.url,
                    headers={"Accept": "application/octet-stream"},
                )
                buffer = io.BytesIO(raw)
                buffer.seek(0)
                return buffer
        raise FileNotFoundError(f"Asset '{key}' not found in release '{self._tag}'")

    # ---------------------------------------------------------------- upload_dir
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ---------------------------------------------------------------- iter_prefix
    def iter_prefix(self, prefix: str):
        full = self._full_key(prefix)
        for asset in self._release.get_assets():
            name = asset.name
            if name.startswith(full.rstrip("/")):
                key = name
                if self._prefix and key.startswith(self._prefix.rstrip("/") + "/"):
                    key = key[len(self._prefix.rstrip("/")) + 1 :]
                yield key

    # ---------------------------------------------------------------- download_prefix
    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    # ---------------------------------------------------------------- from_uri helper
    @classmethod
    def from_uri(cls, uri: str) -> "GithubReleaseStorageAdapter":
        from urllib.parse import urlparse

        p = urlparse(uri)
        org = p.netloc
        repo, tag, *rest = p.path.lstrip("/").split("/", 2)
        prefix = rest[0] if rest else ""

        cfg = load_peagen_toml()
        gh_cfg = cfg.get("storage", {}).get("adapters", {}).get("gh_release", {})

        token = gh_cfg.get("token") or os.getenv("GITHUB_TOKEN", "")

        return cls(
            token=token,
            org=org,
            repo=repo,
            tag=tag,
            prefix=prefix,
        )
