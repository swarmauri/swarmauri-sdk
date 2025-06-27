"""Expose Peagen JSON Schemas as Python dicts."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any, Dict

__all__: list[str] = []


def _load_schema(rel: str) -> Dict[str, Any]:
    with resources.files(__name__).joinpath(rel).open("r", encoding="utf-8") as f:
        return json.load(f)


for _file in resources.files(__name__).iterdir():
    if _file.suffix == ".json":
        _stem = _file.stem  # e.g. doe_spec.schema.v1
        try:
            base, ver = _stem.split(".schema.")
        except ValueError:
            continue
        const = f"{base.upper().replace('.', '_').replace('-', '_')}_{ver.upper().replace('.', '_')}_SCHEMA"
        globals()[const] = _load_schema(_file.name)
        __all__.append(const)

_extras = resources.files(__name__).joinpath("extras")
if _extras.is_dir():
    for _file in _extras.iterdir():
        if _file.suffix == ".json":
            base, ver = _file.stem.split(".schema.")
            const = f"{base.upper().replace('.', '_').replace('-', '_')}_{ver.upper().replace('.', '_')}_SCHEMA"
            globals()[const] = _load_schema(f"extras/{_file.name}")
            __all__.append(const)
