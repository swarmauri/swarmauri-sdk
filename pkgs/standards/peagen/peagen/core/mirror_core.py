"""Helpers for managing git mirrors."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING
import os
import hashlib
import tempfile
import shutil
import fcntl
from contextlib import contextmanager
import httpx

from git import Repo

from peagen.plugins import PluginManager

if TYPE_CHECKING:  # pragma: no cover - import for typing only
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
    pm = PluginManager({})
    GitVCS = pm.get("vcs")
    return GitVCS(
        path,
        remote_url=remote_url,
        mirror_git_url=kwargs.get("mirror_git_url"),
        mirror_git_token=kwargs.get("mirror_git_token"),
        owner=kwargs.get("owner"),
        remotes=kwargs.get("remotes"),
    )


def ensure_repo(
    path: str | Path, remote_url: str | None = None, **kwargs: Any
) -> GitVCS:
    """Initialise ``path`` if needed and return a :class:`GitVCS`."""
    pm = PluginManager({})
    GitVCS = pm.get("vcs")
    return GitVCS(
        path,
        remote_url=remote_url,
        mirror_git_url=kwargs.get("mirror_git_url"),
        mirror_git_token=kwargs.get("mirror_git_token"),
        owner=kwargs.get("owner"),
        remotes=kwargs.get("remotes"),
    )


def add_git_deploy_key(mirror_uri: str, pub_key: str) -> None:
    """Register ``pub_key`` with the remote ``mirror_uri``."""
    res = httpx.post(
        f"{mirror_uri}/deploy_keys",
        json={"key": pub_key, "read_only": False},
        timeout=10.0,
    )
    res.raise_for_status()


def store_fingerprint(repo_uri: str, pub_fp: str) -> None:
    """Persist ``pub_fp`` for ``repo_uri`` under the mirror cache."""
    mirror_root = Path(
        os.getenv("PEAGEN_GIT_MIRROR_DIR", "~/.cache/peagen/mirrors")
    ).expanduser()
    dest = mirror_root / hashlib.sha1(repo_uri.encode()).hexdigest()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "fingerprint").write_text(pub_fp)


def ensure_git_mirror(repo_uri: str) -> Repo:
    """Clone or open a bare mirror for ``repo_uri``."""
    mirror_root = Path(
        os.getenv("PEAGEN_GIT_MIRROR_DIR", "~/.cache/peagen/mirrors")
    ).expanduser()
    mirror_root.mkdir(parents=True, exist_ok=True)
    dest = mirror_root / hashlib.sha1(repo_uri.encode()).hexdigest()
    if dest.exists():
        return Repo(str(dest))
    return Repo.clone_from(repo_uri, dest, mirror=True)


def fetch_git_remote(git_repo: Repo) -> None:
    """Fetch updates for all remotes."""
    git_repo.git.fetch("--all")


def update_git_remote(git_repo: Repo, ssh_cmd: str | None = None) -> None:
    """Push the mirror back to its origin."""
    env = os.environ.copy()
    if ssh_cmd:
        env["GIT_SSH_COMMAND"] = ssh_cmd
    git_repo.git.push("--mirror", env=env)


@contextmanager
def repo_lock(repo_uri: str):
    """Context manager yielding a file lock for ``repo_uri``."""
    from peagen.defaults import LOCK_DIR

    lock_root = Path(os.getenv("PEAGEN_LOCK_DIR", LOCK_DIR)).expanduser()
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / f"{hashlib.sha1(repo_uri.encode()).hexdigest()}.lock"
    with open(lock_path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def add_git_worktree(repo: Repo, ref: str) -> Path:
    """Create a temporary worktree for ``ref`` and return its path."""
    path = Path(tempfile.mkdtemp())
    repo.git.worktree("add", str(path), ref)
    return path


def cleanup_git_worktree(worktree: Path) -> None:
    """Remove a worktree directory."""
    try:
        Repo(str(worktree)).git.worktree("prune")
    except Exception:
        pass
    shutil.rmtree(worktree, ignore_errors=True)


@contextmanager
def ssh_identity(priv_key: str):
    """Yield an SSH command using ``priv_key``."""
    tmp = tempfile.NamedTemporaryFile("w", delete=False)
    tmp.write(priv_key)
    tmp.flush()
    os.chmod(tmp.name, 0o600)
    ssh_cmd = f"ssh -i {tmp.name} -o StrictHostKeyChecking=no"
    try:
        yield ssh_cmd
    finally:
        tmp.close()
        os.remove(tmp.name)


__all__ = [
    "open_repo",
    "ensure_repo",
    "add_git_deploy_key",
    "store_fingerprint",
    "ensure_git_mirror",
    "fetch_git_remote",
    "update_git_remote",
    "repo_lock",
    "add_git_worktree",
    "cleanup_git_worktree",
    "ssh_identity",
]
