from __future__ import annotations

from importlib import metadata
from pathlib import Path

import tomllib

PACKAGE_NAME = "swm-signernametbd"

try:
    __version__ = metadata.version(PACKAGE_NAME)
except metadata.PackageNotFoundError:  # pragma: no cover
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as fh:
        __version__ = tomllib.load(fh)["project"]["version"]

__all__ = ["__version__"]
