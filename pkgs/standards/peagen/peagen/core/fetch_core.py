# peagen/core/fetch_core.py
"""
Pure business-logic for *fetching* a Peagen workspace from a local
directory or remote URI.  No CLI, RPC, or logging dependencies.

Key entry-points
----------------
• fetch_many() – high-level orchestration for multiple URIs
• fetch_single() – one URI → workspace
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import List, Optional


import os

from peagen.plugins.storage_adapters import make_adapter_for_uri  # deprecated
from peagen.core.mirror_core import ensure_repo, open_repo
from peagen.errors import WorkspaceNotFoundError


# ─────────────────────────── low-level helpers ────────────────────────────
def _materialise_workspace(uri: str, dest: Path) -> None:
    """Copy or clone ``uri`` into ``dest``."""
    if uri.startswith("gh://"):
        url = f"https://github.com/{uri[5:]}.git"
        token = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
        if token:
            url = url.replace("https://", f"https://{token}@")
        vcs = ensure_repo(dest, remote_url=url)
        vcs.fetch("HEAD", checkout=True)
        return

    if uri.startswith("git+"):
        url_ref = uri[4:]
        url, _, ref = url_ref.partition("@")
        ref = ref or "HEAD"
        vcs = ensure_repo(dest, remote_url=url)
        try:
            vcs.fetch(ref, checkout=True)
        except Exception:
            vcs.checkout(ref)
        return

    if "://" in uri:
        adapter = make_adapter_for_uri(uri)
        prefix = getattr(adapter, "_prefix", "")
        adapter.download_prefix(prefix, dest)  # type: ignore[attr-defined]
        return

    path = Path(uri)
    if not path.exists():
        raise WorkspaceNotFoundError(uri)
    if path.is_dir():
        shutil.copytree(path, dest, dirs_exist_ok=True)
    else:
        raise ValueError(f"Unsupported workspace URI: {uri}")


# ───────────────────────────── public API ─────────────────────────────────
def fetch_single(
    workspace_uri: str | None = None,
    *,
    dest_root: Path,
    repo: str | None = None,
    ref: str = "HEAD",
) -> dict:
    """Materialise ``workspace_uri`` or ``repo``+``ref`` into ``dest_root``.

    Returns a dictionary containing the workspace path, the fetched commit SHA
    when applicable, and whether the repository was updated during the fetch.
    """
    if repo:
        if "://" not in repo:
            workspace_uri = f"gh://{repo}"
        else:
            workspace_uri = f"git+{repo}@{ref}"
    if workspace_uri and workspace_uri.startswith("gh://") and "@" not in workspace_uri:
        workspace_uri += f"@{ref}"
    if workspace_uri is None:
        raise ValueError("workspace_uri or repo required")

    old_sha = None
    if (dest_root / ".git").exists():
        try:
            old_sha = open_repo(dest_root).repo.head.commit.hexsha
        except Exception:  # pragma: no cover - repo may be empty
            pass

    _materialise_workspace(workspace_uri, dest_root)

    new_sha = None
    updated = True
    if (dest_root / ".git").exists():
        try:
            vcs = open_repo(dest_root)
            new_sha, updated = vcs.repo.head.commit.hexsha, True
            if old_sha is not None:
                updated = old_sha != new_sha
        except Exception:  # pragma: no cover - repo may be missing HEAD
            pass

    return {
        "workspace": str(dest_root),
        "commit": new_sha,
        "updated": updated,
    }


def fetch_many(
    workspace_uris: List[str] | None = None,
    *,
    repo: str | None = None,
    ref: str = "HEAD",
    out_dir: Optional[Path] = None,
    install_template_sets_flag: bool = True,  # ignored, kept for API compat
    no_source: bool = False,  # ignored
) -> dict:
    """Materialise many workspaces under ``out_dir`` (or temp dir)."""
    workspace = (
        out_dir.resolve()
        if out_dir
        else Path(tempfile.mkdtemp(prefix="peagen_ws_")).resolve()
    )
    workspace.mkdir(parents=True, exist_ok=True)

    workspace_uris = workspace_uris or []
    if repo:
        if "://" not in repo:
            workspace_uris = [f"gh://{repo}@{ref}"] + workspace_uris
        else:
            workspace_uris = [f"git+{repo}@{ref}"] + workspace_uris

    results = [fetch_single(uri, dest_root=workspace) for uri in workspace_uris]

    return {"workspace": str(workspace), "fetched": results}
