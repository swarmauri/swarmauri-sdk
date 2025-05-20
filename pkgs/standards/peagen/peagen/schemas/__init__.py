# peagen/schemas/__init__.py
"""
Expose manifest-v3 JSON Schema as a Python dict.

Import with:
    from peagen.schemas import MANIFEST_V3_SCHEMA
"""

from __future__ import annotations
import json, importlib.resources as res

MANIFEST_V3_SCHEMA = json.loads(
    res.files(__package__)
       .joinpath("manifest.schema.v3.json")
       .read_text(encoding="utf-8")
)

__all__ = ["MANIFEST_V3_SCHEMA"]
