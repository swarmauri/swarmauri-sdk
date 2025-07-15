"""
peagen.core.fetch_core
──────────────────────
Materialise one or more Git repositories at a specific *ref* into **work-trees**.
All mirror provisioning (org / mirror creation) is done by the gateway, so this
module is only responsible for:

1. Refreshing the already-existing mirror (`git fetch --all`).
2. Creating an isolated work-tree for the caller.
3. Returning the path + commit SHA.

Concurrency safety is provided by ``repo_lock(repo_url)``.
"""

from __future__ import annotations

import hashlib
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from peagen.defaults import ROOT_DIR
from peagen.core.git_repo_core import (
    open_repo,
    fetch_git_remote,
    repo_lock,
)

# ───────────────────────── helper: deterministic paths ────────────
def _mirror_path(repo_url: str) -> Path:
    """Return the filesystem path of the bare mirror for *repo_url*."""
    repo_hash = hashlib.sha1(repo_url.encode()).hexdigest()[:12]
    return Path(ROOT_DIR).expanduser() / "mirrors" / repo_hash


def _worktree_path(
    repo_url: str,
    ref: str,
    base: Path,
    tag: str | None = None,
) -> Path:
    """Compute work-tree path under *base*."""
    repo_hash = hashlib.sha1(repo_url.encode()).hexdigest()[:12]
    ref_dir = ref.replace("/", "_")
    tag = tag or uuid.uuid4().hex[:8]
    return base / repo_hash / ref_dir / tag


# ─────────────────────────── public API ───────────────────────────
def fetch_single(
    *,
    repo: str,
    ref: str = "HEAD",
    dest_root: Path,
) -> dict:
    """
    Ensure *repo* is fetched and checked out at *ref* inside *dest_root*.

    Parameters
    ----------
    repo : str
        Clone URL (https / ssh) of the upstream repository.
    ref : str, optional
        Branch, tag, or commit SHA. Defaults to "HEAD".
    dest_root : Path
        Directory that will become the **work-tree**. Any pre-existing content
        will be removed first.

    Returns
    -------
    dict – {"workspace": <str>, "commit": <sha>, "updated": <bool>}
    """
    if not repo:
        raise ValueError("parameter 'repo' must be supplied")

    mirror = _mirror_path(repo)
    dest_root = dest_root.expanduser().resolve()

    with repo_lock(repo):
        vcs = open_repo(mirror, remote_url=repo)
        fetch_git_remote(vcs)

        # Remove any stale work-tree at dest_root
        if dest_root.exists():
            shutil.rmtree(dest_root, ignore_errors=True)
        dest_root.parent.mkdir(parents=True, exist_ok=True)

        # Create fresh work-tree
        vcs.git.worktree("add", str(dest_root), ref)
        commit_sha = vcs.repo.commit(ref).hexsha

    return {"workspace": str(dest_root), "commit": commit_sha, "updated": True}


def fetch_many(
    repos: List[str],
    *,
    ref: str = "HEAD",
    out_dir: Optional[Path] = None,
) -> dict:
    """
    Materialise **each** repository in *repos* at *ref* into its own work-tree.

    Parameters
    ----------
    repos : List[str]
        List of clone URLs.
    ref : str, optional
        Branch, tag, or SHA applied to all repos. Defaults to "HEAD".
    out_dir : Path | None
        Root directory under which work-trees will be created.  If None,
        a temporary directory is generated inside the Peagen root.

    Returns
    -------
    dict – {"workspace": <root>, "fetched": [<fetch_single results>]}
    """
    base = (
        out_dir.expanduser().resolve()
        if out_dir
        else Path(ROOT_DIR).expanduser()
        / "worktrees"
        / f"bulk_{uuid.uuid4().hex[:8]}"
    )
    base.mkdir(parents=True, exist_ok=True)

    results = []
    for repo_url in repos:
        wtree_path = _worktree_path(repo_url, ref, base)
        res = fetch_single(repo=repo_url, ref=ref, dest_root=wtree_path)
        results.append(res)

    return {"workspace": str(base), "fetched": results}
