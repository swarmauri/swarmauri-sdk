"""Read optional project configuration without depending on a plugin host."""

from __future__ import annotations

import os
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def load_filter_config() -> dict:
    """Read PEAGEN_CONFIG or the nearest peagen.toml if present."""
    configured = os.environ.get("PEAGEN_CONFIG")
    if configured:
        path = Path(configured).expanduser()
        with path.open("rb") as stream:
            return tomllib.load(stream)
    current = Path.cwd()
    for directory in (current, *current.parents):
        path = directory / "peagen.toml"
        if path.is_file():
            with path.open("rb") as stream:
                return tomllib.load(stream)
    return {}
