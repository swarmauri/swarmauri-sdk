from __future__ import annotations

from pathlib import Path as FilePath

FAVICON_PATH = FilePath(__file__).resolve().parents[1] / "deps" / "favicon.svg"

__all__ = ["FAVICON_PATH"]
