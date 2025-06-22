"""Shared helpers for Typer commands."""

from __future__ import annotations

import os
import pathlib
import tempfile
from contextlib import contextmanager
import shutil

from swarmauri_standard.loggers.Logger import Logger

logger = Logger(name=__name__)


# ─────────────────────────────────────────────────────────────────────────────
# 0. temp_workspace
# ─────────────────────────────────────────────────────────────────────────────
@contextmanager
def temp_workspace(prefix: str = "peagen_"):
    """Yield a temporary directory that is removed on exit."""
    dirpath = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield dirpath  # ←  every path you write will be under here
    finally:
        try:
            shutil.rmtree(dirpath)
        except FileNotFoundError:
            # Already removed – fine.
            pass
        except OSError as exc:
            logger.warning(f"Workspace cleanup failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. PathOrURI
# ─────────────────────────────────────────────────────────────────────────────
class PathOrURI(str):
    """
    A very thin wrapper that normalises user input:

        * '~/foo'      -> 'file:///home/user/foo'
        * 'C:\\bar'    -> 'file:///C:/bar'
        * 's3://...'   -> unchanged
        * 'file://...' -> unchanged
    """

    def __new__(cls, value: str | os.PathLike) -> "PathOrURI":
        return super().__new__(cls, cls._normalise(value))

    # ---------------------------------------------------------------- private
    @staticmethod
    def _normalise(value: str | os.PathLike) -> str:
        value = str(value)

        # already a URI?
        if "://" in value:
            return value

        # expand user and resolve relative path, return the *plain* path
        p = pathlib.Path(value).expanduser().resolve()
        return str(p)  # no file:// prefix
