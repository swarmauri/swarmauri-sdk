from __future__ import annotations

"""Storage adapter using a git HTTP server."""

import io
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urlparse

import requests


class GitHttpStorageAdapter:
    """Upload artifacts via ``git push`` and fetch them with HTTP GET."""

    def __init__(self, repo_url: str, branch: str = "main", *, prefix: str = "") -> None:
        self._repo_url = repo_url.rstrip("/")
        self._branch = branch
        self._prefix = prefix.lstrip("/")

    # ------------------------------------------------------------------ helpers
    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    @property
    def root_uri(self) -> str:
        base = f"git+{self._repo_url}#{self._branch}"
        if self._prefix:
            return f"{base}/{self._prefix.rstrip('/')}".rstrip("/") + "/"
        return base + "/"

    # -------------------------------------------------------------------- upload
    def upload(self, key: str, data: BinaryIO) -> str:
        """Push ``data`` to the repository under ``key`` and return the URI."""
        full = self._full_key(key)
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "clone", self._repo_url, tmp], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "-C", tmp, "checkout", self._branch], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            dest = Path(tmp, full)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as fh:
                shutil.copyfileobj(data, fh)
            subprocess.run(["git", "-C", tmp, "add", dest.relative_to(tmp).as_posix()], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "-C", tmp, "commit", "-m", f"Add {full}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "-C", tmp, "push", "origin", self._branch], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return f"{self.root_uri}{key.lstrip('/')}"

    # ------------------------------------------------------------------- download
    def download(self, key: str) -> BinaryIO:
        """Return ``BytesIO`` contents of ``key`` via HTTP GET."""
        full = self._full_key(key)
        url = f"{self._repo_url}/raw/{self._branch}/{full}"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise FileNotFoundError(f"{url}: {resp.status_code}")
        buf = io.BytesIO(resp.content)
        buf.seek(0)
        return buf

    # ------------------------------------------------------------------ from_uri
    @classmethod
    def from_uri(cls, uri: str) -> "GitHttpStorageAdapter":
        p = urlparse(uri)
        repo_scheme = p.scheme.split("+", 1)[1] if "+" in p.scheme else p.scheme
        repo_url = f"{repo_scheme}://{p.netloc}{p.path}"
        branch = "main"
        prefix = ""
        if p.fragment:
            branch_part, _, prefix = p.fragment.partition("/")
            branch = branch_part or branch
        return cls(repo_url=repo_url, branch=branch, prefix=prefix)


__all__ = ["GitHttpStorageAdapter"]
