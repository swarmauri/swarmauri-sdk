from __future__ import annotations

from pathlib import Path
from git import Repo
from git.exc import InvalidGitRepositoryError

from peagen.errors import GitRemoteMissingError


def require_origin(path: str | Path = ".") -> None:
    """Raise :class:`GitRemoteMissingError` if 'origin' is missing."""
    try:
        repo = Repo(Path(path).resolve(), search_parent_directories=True)
    except InvalidGitRepositoryError:
        return
    if "origin" not in [r.name for r in repo.remotes]:
        raise GitRemoteMissingError("Remote 'origin' is not configured")
