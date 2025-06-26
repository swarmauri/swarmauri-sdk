from __future__ import annotations

from pathlib import Path
from typing import Tuple, Optional
import tempfile
import os
import shutil

from peagen.core.fetch_core import fetch_single


def fetch_repo(
    repo: Optional[str], ref: str = "HEAD"
) -> Tuple[Optional[Path], Optional[Path]]:
    """Clone *repo* at *ref* into a temp directory and return (tmp_dir, prev_cwd)."""
    if not repo:
        return None, None
    tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
    fetch_single(repo=repo, ref=ref, dest_root=tmp_dir)
    prev_cwd = Path.cwd()
    os.chdir(tmp_dir)
    return tmp_dir, prev_cwd


def cleanup_repo(tmp_dir: Optional[Path], prev_cwd: Optional[Path]) -> None:
    """Return to *prev_cwd* and remove *tmp_dir* if provided."""
    if not tmp_dir or not prev_cwd:
        return
    os.chdir(prev_cwd)
    shutil.rmtree(tmp_dir, ignore_errors=True)
