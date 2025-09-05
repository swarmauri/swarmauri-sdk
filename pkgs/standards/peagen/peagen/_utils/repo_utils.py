from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
import tempfile
import os
import shutil

from peagen.core.fetch_core import fetch_single


@contextmanager
def maybe_clone_repo(
    repo: Optional[str], ref: str = "HEAD"
) -> Iterator[Optional[Path]]:
    """Clone *repo* at *ref* into a temp dir and chdir to it if provided."""
    if repo:
        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_dir)
        prev_cwd = Path.cwd()
        os.chdir(tmp_dir)
        try:
            yield tmp_dir
        finally:
            os.chdir(prev_cwd)
            shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        yield None
