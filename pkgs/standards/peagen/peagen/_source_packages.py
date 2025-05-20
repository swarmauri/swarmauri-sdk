"""Helpers to copy or clone external packages into a Peagen workspace."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer


# ---------------------------------------------------------------------------
# git helpers
# ---------------------------------------------------------------------------
def _git_clone_to(dest: Path, uri: str, ref: Optional[str] = None) -> None:
    """Clone a Git repository to *dest* at the given ref."""
    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [uri, str(dest)]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as exc:
        typer.echo(f"[ERROR] git clone failed: {exc}")
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# materialise a single package
# ---------------------------------------------------------------------------
def _materialise_source_pkg(
    pkg_spec: Dict[str, Any],
    workspace: Path,
    storage_adapter: Optional[Any] = None,
) -> Path:
    """Copy or clone *pkg_spec* into the workspace and upload via adapter."""
    dest = workspace / pkg_spec["dest"]
    if dest.exists():
        shutil.rmtree(dest)

    typ = pkg_spec.get("type")
    if typ == "git":
        _git_clone_to(dest, pkg_spec["uri"], pkg_spec.get("ref"))
    elif typ == "local":
        src = Path(pkg_spec["path"]).expanduser().resolve()
        shutil.copytree(src, dest)
    else:
        raise ValueError(f"Unknown source package type: {typ}")

    if storage_adapter:
        storage_adapter.upload_dir(dest, prefix=str(dest.relative_to(workspace)))

    return dest


# ---------------------------------------------------------------------------
# convenience: materialise many packages
# ---------------------------------------------------------------------------
def materialise_packages(
    packages: List[Dict[str, Any]],
    workspace: Path,
    storage_adapter: Optional[Any] = None,
) -> List[Path]:
    dests = []
    for spec in packages:
        dests.append(_materialise_source_pkg(spec, workspace, storage_adapter))
    return dests
