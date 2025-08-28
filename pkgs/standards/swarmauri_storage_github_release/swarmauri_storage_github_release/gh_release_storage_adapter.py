"""Storage adapter backed by GitHub Releases."""

from __future__ import annotations

from pydantic import SecretStr

import io
import os
import shutil
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase

from peagen._utils.config_loader import load_peagen_toml
from github import Github, UnknownObjectException


@ComponentBase.register_type(StorageAdapterBase, "GithubReleaseStorageAdapter")
class GithubReleaseStorageAdapter(StorageAdapterBase):
    """Storage adapter that uses GitHub Releases to store and retrieve assets."""

    def __init__(
        self,
        token: SecretStr | str,
        org: str,
        repo: str,
        tag: str,
        *,
        release_name: Optional[str] = None,
        message: str = "",
        draft: bool = False,
        prerelease: bool = False,
        prefix: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        token_val = token.get_secret_value() if isinstance(token, SecretStr) else token
        self._client = Github(token_val)
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

    # ----------------------------------------------------------------- helpers
    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    @property
    def root_uri(self) -> str:
        """Return the base ghrel:// URI for this adapter."""
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

    # ------------------------------------------------------------------- public
    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload ``data`` under ``key`` as a release asset and return the artifact URI."""
        key = self._full_key(key)

        data.seek(0)
        content = data.read()

        for asset in self._release.get_assets():
            if asset.name == key:
                asset.delete_asset()
                break

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content)
            tmp.flush()
            self._release.upload_asset(path=tmp.name, name=key, label=key)

        return f"{self.root_uri}{key.lstrip('/')}"

    def download(self, key: str) -> BinaryIO:
        """Return the bytes of asset ``key`` as a BytesIO object."""
        key = self._full_key(key)

        for asset in self._release.get_assets():
            if asset.name == key:
                _, raw = self._client._Github__requester.requestBytes(
                    "GET",
                    asset.url,
                    headers={"Accept": "application/octet-stream"},
                )
                buf = io.BytesIO(raw)
                buf.seek(0)
                return buf
        raise FileNotFoundError(f"Asset '{key}' not found in release '{self._tag}'")

    # --------------------------------------------------------------- convenience
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Upload all files under *src* using an optional *prefix*."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    def iter_prefix(self, prefix: str):
        """Yield asset keys under *prefix*."""
        full = self._full_key(prefix)
        for asset in self._release.get_assets():
            name = asset.name
            if name.startswith(full.rstrip("/")):
                key = name
                if self._prefix and key.startswith(self._prefix.rstrip("/") + "/"):
                    key = key[len(self._prefix.rstrip("/")) + 1 :]
                yield key

    def download_dir(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download all assets under *prefix* into *dest_dir*."""
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    # --------------------------------------------------------------------- class
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


__all__ = ["GithubReleaseStorageAdapter"]
