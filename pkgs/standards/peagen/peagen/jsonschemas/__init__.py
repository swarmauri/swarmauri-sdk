"""Expose Peagen JSON Schemas as Python dictionaries."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import List

__all__: List[str] = []

_pkg_files = files(__name__)

for _path in _pkg_files.rglob("*.json"):
    if _path.name == "__init__.py":
        continue
    name_part, version_part_json = _path.name.split(".schema.")
    version_part = version_part_json[: -len(".json")]
    const_name = (
        f"{name_part.upper().replace('-', '_')}"
        f"_{version_part.upper().replace('.', '_')}_SCHEMA"
    )
    with _path.open("r", encoding="utf-8") as f:
        globals()[const_name] = json.load(f)
    __all__.append(const_name)

__all__.sort()
