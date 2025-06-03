"""Storage adapter using GitHub repositories."""

from __future__ import annotations
from pydantic import SecretStr
import io
import os
import shutil
import base64
from pathlib import Path
from typing import BinaryIO

from peagen.cli_common import load_peagen_toml
from github import Github
from github.GithubException import GithubException


class GithubStorageAdapter:
    """
    Storage adapter that implements upload and download using GitHub repositories.

    Requires a GitHub personal access token with repo access.
    Supports uploading both text and binary (via base64 encoding).
    """

    def __init__(
        self,
        token: SecretStr,
        org: str,
        repo: str,
        *,
        branch: str = "main",
        prefix: str = "",
    ):
        # Authenticate to GitHub
        self._client = Github(token.get_secret_value())
        # Get the target repository
        self._repo = self._client.get_organization(org).get_repo(repo)
        self._branch = branch
        self._prefix = prefix.lstrip("/")

    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    # NEW ────────────────────────────────────────────────────────────────
    @property
    def root_uri(self) -> str:
        """
        Location prefix used by Peagen manifests and evaluators.
        Example:  gh://my-org/my-repo/main/
        """
        base = f"gh://{self._repo.full_name}/{self._branch}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    def upload(self, key: str, data: BinaryIO) -> None:
        """
        Uploads data to the repository at the given key (path).

        If the file already exists, it will be updated; otherwise, it will be created.
        Binary data is base64-encoded automatically.
        """
        key = self._full_key(key)

        # Read all data
        data.seek(0)
        content_bytes = data.read()

        # Determine if binary (non-UTF-8) or text
        try:
            content_str = content_bytes.decode("utf-8")
            is_binary = False
        except UnicodeDecodeError:
            # Binary file: base64 encode
            content_str = base64.b64encode(content_bytes).decode("utf-8")
            is_binary = True

        # Prepare commit message
        commit_msg = f"Upload {key}"
        try:
            # Check if file exists
            existing = self._repo.get_contents(key, ref=self._branch)
            # Update
            if is_binary:
                self._repo.update_file(
                    path=key,
                    message=commit_msg,
                    content=content_str,
                    sha=existing.sha,
                    branch=self._branch,
                )
            else:
                self._repo.update_file(
                    path=key,
                    message=commit_msg,
                    content=content_str,
                    sha=existing.sha,
                    branch=self._branch,
                )
        except GithubException as exc:
            # Create new file
            if exc.status == 404:
                self._repo.create_file(
                    path=key,
                    message=commit_msg,
                    content=content_str,
                    branch=self._branch,
                )
            else:
                raise

    def download(self, key: str) -> BinaryIO:
        """
        Downloads the file from the repository at the given key (path) and
        returns it as a BytesIO object.
        """
        key = self._full_key(key)
        try:
            content_file = self._repo.get_contents(key, ref=self._branch)
            # decoded_content gives raw bytes for both text and binary
            raw_bytes = content_file.decoded_content  # type: ignore
            buffer = io.BytesIO(raw_bytes)
            buffer.seek(0)
            return buffer
        except GithubException as exc:
            if exc.status == 404:
                raise FileNotFoundError(
                    f"{key}: not found in {self._repo.full_name}@{self._branch}"
                )
            raise

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
        full = self._full_key(prefix).rstrip("/")
        stack = [full] if full else [""]
        while stack:
            current = stack.pop()
            try:
                items = self._repo.get_contents(current or "", ref=self._branch)
            except GithubException as exc:
                if exc.status == 404:
                    continue
                raise
            if not isinstance(items, list):
                items = [items]
            for item in items:
                if item.type == "dir":
                    stack.append(item.path)
                else:
                    key = item.path
                    if self._prefix and key.startswith(self._prefix.rstrip("/") + "/"):
                        key = key[len(self._prefix.rstrip("/")) + 1 :]
                    if key.startswith(prefix.rstrip("/")):
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
    def from_uri(cls, uri: str) -> "GithubStorageAdapter":
        from urllib.parse import urlparse

        p = urlparse(uri)
        org = p.netloc
        parts = p.path.lstrip("/").split("/", 2)
        repo = parts[0]
        branch = parts[1] if len(parts) > 1 else "main"
        prefix = parts[2] if len(parts) > 2 else ""

        cfg = load_peagen_toml()
        gh_cfg = cfg.get("storage", {}).get("adapters", {}).get("github", {})

        token = gh_cfg.get("token") or os.getenv("GITHUB_TOKEN", "")

        return cls(
            token=token,
            org=org,
            repo=repo,
            branch=branch,
            prefix=prefix,
        )
