"""Helpers for managing git mirrors."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING
import os
import hashlib
import tempfile
import shutil
from filelock import FileLock
from contextlib import contextmanager

from git import Repo

from peagen.plugins import PluginManager
from peagen.plugin_manager import resolve_plugin_spec
from peagen import defaults

if TYPE_CHECKING:  # pragma: no cover - import for typing only
    from peagen.plugins.vcs import GitVCS


# ───────── git repo convenience      ────────────────────────────


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
    pm = PluginManager(defaults.CONFIG)
    cfg = pm._group_cfg("vcs")
    name = cfg.get("default_vcs")
    params = cfg.get("adapters", {}).get(name, {})
    params = {
        **params,
        "remote_url": remote_url,
        "mirror_git_url": kwargs.get("mirror_git_url"),
        "mirror_git_token": kwargs.get("mirror_git_token"),
        "owner": kwargs.get("owner"),
        "remotes": kwargs.get("remotes"),
    }
    GitVCS = resolve_plugin_spec("vcs", name)
    return GitVCS(path, **params)


# ───────── git remote ops      ────────────────────────────


def fetch_git_remote(git_repo: Repo) -> None:
    """Fetch updates for all remotes."""
    git_repo.git.fetch("--all")


def update_git_remote(git_repo: Repo, ssh_cmd: str | None = None) -> None:
    """Push the mirror back to its origin."""
    env = os.environ.copy()
    if ssh_cmd:
        env["GIT_SSH_COMMAND"] = ssh_cmd
    git_repo.git.push("--mirror", env=env)


# ───────── worker repo lock      ────────────────────────────


@contextmanager
def repo_lock(repo_uri: str):
    """Context manager yielding a file lock for ``repo_uri``."""
    from peagen.defaults import lock_dir

    lock_root = lock_dir()
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / f"{hashlib.sha1(repo_uri.encode()).hexdigest()}.lock"
    file_lock = FileLock(lock_path)
    with file_lock:
        yield


# ───────── worker worktree   ────────────────────────────


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


# ───────── worker ssh identity  ────────────────────────────


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


# ───────── exports  ────────────────────────────
