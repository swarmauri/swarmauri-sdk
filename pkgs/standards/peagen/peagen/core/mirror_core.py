"""Helpers for managing git mirrors."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from peagen.plugins.vcs import GitVCS


def open_repo(path: str | Path, remote_url: str | None = None, **kwargs: Any) -> GitVCS:
    """Open a repository at ``path``.

    Parameters
    ----------
    path:
        Filesystem location of the repository.
    remote_url:
        Optional remote URL to clone if the repository does not exist.
    **kwargs:
        Additional options forwarded to :class:`GitVCS`.
    """
    return GitVCS(
        path,
        remote_url=remote_url,
        mirror_git_url=kwargs.get("mirror_git_url"),
        mirror_git_token=kwargs.get("mirror_git_token"),
        owner=kwargs.get("owner"),
    )


def ensure_repo(
    path: str | Path, remote_url: str | None = None, **kwargs: Any
) -> GitVCS:
    """Initialise ``path`` if needed and return a :class:`GitVCS`."""
    return GitVCS(
        path,
        remote_url=remote_url,
        mirror_git_url=kwargs.get("mirror_git_url"),
        mirror_git_token=kwargs.get("mirror_git_token"),
        owner=kwargs.get("owner"),
    )


__all__ = ["open_repo", "ensure_repo"]
