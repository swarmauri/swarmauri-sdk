"""Utilities for working with Git repositories."""

from pathlib import Path
from typing import Optional

from git import InvalidGitRepositoryError, NoSuchPathError, Repo


def get_repo(path: str | Path, remote_url: Optional[str] = None) -> Repo:
    """Return a Git repository, initializing one if necessary.

    Args:
        path: Target directory for the repository.
        remote_url: Optional URL for the ``origin`` remote when creating a new
            repository.

    Returns:
        Repo: Initialized or existing Git repository.
    """

    repo_path = Path(path)
    try:
        repo = Repo(repo_path)
    except (InvalidGitRepositoryError, NoSuchPathError):
        repo = Repo.init(repo_path)
        if remote_url:
            repo.create_remote("origin", remote_url)
    return repo
