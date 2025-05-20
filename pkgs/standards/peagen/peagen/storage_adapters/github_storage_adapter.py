from __future__ import annotations
from pydantic import SecretStr
import io
import base64
from typing import BinaryIO
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
    ):
        # Authenticate to GitHub
        self._client = Github(token.get_secret_value())
        # Get the target repository
        self._repo = self._client.get_organization(org).get_repo(repo)
        self._branch = branch

    # NEW ────────────────────────────────────────────────────────────────
    @property
    def root_uri(self) -> str:
        """
        Location prefix used by Peagen manifests and evaluators.
        Example:  gh://my-org/my-repo/main/
        """
        return f"gh://{self._repo.full_name}/{self._branch}/"

    def upload(self, key: str, data: BinaryIO) -> None:
        """
        Uploads data to the repository at the given key (path).

        If the file already exists, it will be updated; otherwise, it will be created.
        Binary data is base64-encoded automatically.
        """
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
        try:
            content_file = self._repo.get_contents(key, ref=self._branch)
            # decoded_content gives raw bytes for both text and binary
            raw_bytes = content_file.decoded_content  # type: ignore
            buffer = io.BytesIO(raw_bytes)
            buffer.seek(0)
            return buffer
        except GithubException as exc:
            if exc.status == 404:
                raise FileNotFoundError(f"{key}: not found in {self._repo.full_name}@{self._branch}")
            raise
