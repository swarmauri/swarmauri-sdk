"""
peagen.core.fetch_core
──────────────────────
Materialise a *single* Git repository + ref (and optionally many) into a local
workspace.  All mirror prep is already handled by the gateway, so this module
only needs to clone/fetch and check out the requested ref.

Key entry-points
----------------
• fetch_single() – repo + ref → workspace
• fetch_many()   – convenience wrapper for multiple repos
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Optional

from peagen.core.git_repo_core import (
    open_repo,  # pluggable VCS adapter
    repo_lock,  # cross-process file lock
)


# ─────────────────────────── helpers ──────────────────────────────
def _checkout(repo_url: str, ref: str, dest: Path) -> str | None:
    """
    Clone or update *repo_url* into *dest* and checkout *ref*.

    Returns the checked-out commit SHA (or None on bare copy errors).
    """
    with repo_lock(repo_url):  # requirement #4
        vcs = open_repo(dest, remote_url=repo_url)  # requirement #3
        try:
            vcs.fetch(ref, checkout=True)  # update if remote already cloned
        except Exception:
            vcs.checkout(ref)
        try:
            return vcs.repo.head.commit.hexsha
        except Exception:
            return None


# ─────────────────────────── public API ───────────────────────────
def fetch_single(
    *,
    repo: str,
    ref: str = "HEAD",
    dest_root: Path,
) -> dict:
    """
    Ensure *repo* is present in *dest_root* and checked out at *ref*.

    Parameters
    ----------
    repo : str
        Clone URL understood by Git (https, ssh, or local path).
    ref : str, optional
        Branch, tag, or SHA.  Defaults to "HEAD".
    dest_root : Path
        Destination directory for the workspace.

    Returns
    -------
    dict  –  {"workspace": <str>, "commit": <sha|None>, "updated": <bool>}
    """
    if not repo:
        raise ValueError("parameter 'repo' must be supplied")

    # Resolve previous HEAD (if any) to detect updates
    old_sha = None
    if (dest_root / ".git").exists():
        try:
            old_sha = open_repo(dest_root).repo.head.commit.hexsha
        except Exception:
            pass

    new_sha = _checkout(repo, ref, dest_root)

    updated = new_sha is not None and new_sha != old_sha
    return {"workspace": str(dest_root), "commit": new_sha, "updated": updated}


def fetch_many(
    repos: List[str],
    *,
    ref: str = "HEAD",
    out_dir: Optional[Path] = None,
) -> dict:
    """
    Clone / update *repos* under *out_dir* (or a temp dir) at *ref*.

    Parameters
    ----------
    repos : List[str]
        List of clone URLs.
    ref : str, optional
        Branch, tag, or SHA applied to **all** repos.  Defaults to "HEAD".
    out_dir : Path | None
        Workspace root.  If None, a temp directory is created.

    Returns
    -------
    dict – {"workspace": <root>, "fetched": [<fetch_single results>]}
    """
    workspace = (
        out_dir.resolve()
        if out_dir
        else Path(tempfile.mkdtemp(prefix="peagen_ws_")).resolve()
    )
    workspace.mkdir(parents=True, exist_ok=True)

    results = [fetch_single(repo=r, ref=ref, dest_root=workspace) for r in repos]
    return {"workspace": str(workspace), "fetched": results}
