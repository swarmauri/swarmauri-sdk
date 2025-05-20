"""Helpers to copy or clone external packages into a Peagen workspace."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer


# ────────────────────────────────────────────────────────────────────────────
# git helpers
# ────────────────────────────────────────────────────────────────────────────
def _git_clone_to(dest: Path, uri: str, ref: Optional[str] = None) -> None:
    """Shallow-clone *uri* into *dest* at *ref* (tag/branch/SHA)."""
    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [uri, str(dest)]

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"     # never wait for creds

    try:
        subprocess.check_call(cmd, env=env)
    except subprocess.CalledProcessError as exc:
        typer.echo(f"[ERROR] git clone failed: {exc}")
        raise typer.Exit(1)


def _strip_git_dir(pkg_dir: Path) -> None:
    """
    Delete the .git directory inside *pkg_dir*, clearing read-only bits so that
    Windows can remove pack/idx files without WinError 5.
    """
    git_dir = pkg_dir / ".git"
    if not git_dir.exists():
        return

    def _on_rm_error(fn, path, exc_info):
        # clear read-only attr and retry
        os.chmod(path, stat.S_IWRITE)
        fn(path)

    # Some AV tools hold locks briefly; retry a couple of times.
    for attempt in range(3):
        try:
            shutil.rmtree(git_dir, onerror=_on_rm_error)
            return
        except PermissionError:
            time.sleep(0.5)

    typer.echo(f"WARNING: could not fully delete {git_dir}; "
               "workspace cleanup may be slow")


# ────────────────────────────────────────────────────────────────────────────
# materialise a single package
# ────────────────────────────────────────────────────────────────────────────
def _materialise_source_pkg(
    pkg_spec: Dict[str, Any],
    workspace: Path,
    upload: bool = False,
    storage_adapter: Optional[Any] = None,
) -> Path:
    """
    Copy or clone *pkg_spec* into the workspace and (optionally) upload.

    pkg_spec keys:
        type:  "git" | "local"
        uri / path
        ref   (git only)
        dest  (relative to workspace)
    """
    dest = workspace / pkg_spec["dest"]
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)

    typ = pkg_spec.get("type")
    if typ == "git":
        _git_clone_to(dest, pkg_spec["uri"], pkg_spec.get("ref"))
    elif typ == "local":
        src = Path(pkg_spec["path"]).expanduser().resolve()
        shutil.copytree(src, dest)
    else:
        raise ValueError(f"Unknown source package type: {typ!r}")

    # Remove .git to avoid WinError 5 during workspace cleanup
    _strip_git_dir(dest)

    # Optional upload (disabled by default)
    if upload and storage_adapter:
        _sync_dir(dest, storage_adapter, prefix=str(dest.relative_to(workspace)))

    return dest


def _sync_dir(root: Path, adapter: Any, *, prefix: str = "") -> None:
    """
    Portable fallback for adapters that only implement `upload()`.
    Uses adapter.upload_dir() if available, else walks the tree.
    """
    if hasattr(adapter, "upload_dir"):
        adapter.upload_dir(root, prefix=prefix)
        return

    for file_path in root.rglob("*"):
        if file_path.is_file():
            key = f"{prefix}/{file_path.relative_to(root)}"
            with file_path.open("rb") as fh:
                adapter.upload(str(key), fh)


# ────────────────────────────────────────────────────────────────────────────
# convenience: materialise many packages
# ────────────────────────────────────────────────────────────────────────────
def materialise_packages(
    packages: List[Dict[str, Any]],
    workspace: Path,
    storage_adapter: Optional[Any] = None,
    *,
    upload: bool = False,
) -> List[Path]:
    """Clone / copy a list of source packages into *workspace*."""
    dests: List[Path] = []
    for spec in packages:
        dests.append(
            _materialise_source_pkg(
                spec,
                workspace,
                upload=upload,
                storage_adapter=storage_adapter,
            )
        )
    return dests
