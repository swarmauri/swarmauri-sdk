"""Common utilities for non-CLI components."""

from __future__ import annotations

import os
import pathlib
import tempfile
import shutil
import logging
from contextlib import contextmanager
from typing import Any, Callable

__all__ = ["temp_workspace", "PathOrURI"]


@contextmanager
def temp_workspace(prefix: str = "peagen_"):
    """Yield a temporary directory that is removed on exit."""
    dirpath = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield dirpath
    finally:
        try:
            shutil.rmtree(dirpath)
        except FileNotFoundError:
            pass
        except OSError as exc:
            logging.warning(f"Workspace cleanup failed: {exc}")


class PathOrURI(str):
    """Normalise a filesystem path or return URIs unchanged."""

    def __new__(cls, value: str | os.PathLike) -> "PathOrURI":
        return super().__new__(cls, cls._normalise(value))

    @staticmethod
    def _normalise(value: str | os.PathLike) -> str:
        value = str(value)
        if "://" in value:
            return value
        p = pathlib.Path(value).expanduser().resolve()
        return str(p)
