# peagen/schemas/__init__.py
"""
Expose manifest-v3 JSON Schema as a Python dict.

Import with:
    from peagen.schemas import MANIFEST_V3_SCHEMA
"""

from __future__ import annotations
import json
import importlib.resources as res

MANIFEST_V3_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("manifest.schema.v3.json")
    .read_text(encoding="utf-8")
)

MANIFEST_V3_1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("manifest.schema.v3.1.json")
    .read_text(encoding="utf-8")
)

PEAGEN_TOML_V1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("peagen.toml.schema.v1.json")
    .read_text(encoding="utf-8")
)

PEAGEN_TOML_V1_1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("peagen.toml.schema.v1.1.0.json")
    .read_text(encoding="utf-8")
)

DOE_SPEC_V1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("doe_spec.schema.v1.json")
    .read_text(encoding="utf-8")
)


PTREE_V1_SCHEMA = json.loads(
    res.files(__package__).joinpath("ptree.schema.v1.json").read_text(encoding="utf-8")
)

PROJECTS_PAYLOAD_V1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("projects_payload.schema.v1.json")
    .read_text(encoding="utf-8")
)

EVENT_V1_SCHEMA = json.loads(
    res.files(__package__).joinpath("event.schema.v1.json").read_text(encoding="utf-8")
)

# ── EXTRAS schemas ─────────────────────────────────────────────
_extras_pkg = res.files(__package__).joinpath("extras")
EXTRAS_SCHEMAS = {
    fp.name.replace(".schema.v1.json", ""): json.loads(fp.read_text(encoding="utf-8"))
    for fp in _extras_pkg.iterdir()
    if fp.name.endswith(".schema.v1.json")
}


__all__ = [
    "MANIFEST_V3_SCHEMA",
    "MANIFEST_V3_1_SCHEMA",
    "PEAGEN_TOML_V1_SCHEMA",
    "PEAGEN_TOML_V1_1_SCHEMA",
    "DOE_SPEC_V1_SCHEMA",
    "PTREE_V1_SCHEMA",
    "PROJECTS_PAYLOAD_V1_SCHEMA",
    "EVENT_V1_SCHEMA",
    "EXTRAS_SCHEMAS",
]
