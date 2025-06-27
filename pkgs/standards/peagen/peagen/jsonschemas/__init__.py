# peagen/jsonschemas/__init__.py
"""Expose Peagen JSON Schemas as Python dicts."""

from __future__ import annotations
import json
import importlib.resources as res


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

DOE_SPEC_V1_1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("doe_spec.schema.v1.1.json")
    .read_text(encoding="utf-8")
)

DOE_SPEC_V2_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("doe_spec.schema.v2.json")
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

EVOLVE_SPEC_V1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("evolve_spec.schema.v1.json")
    .read_text(encoding="utf-8")
)

try:
    EVOLVE_SPEC_V2_SCHEMA = json.loads(
        res.files(__package__)
        .joinpath("evolve_spec.schema.v2.0.0.json")
        .read_text(encoding="utf-8")
    )
except Exception:
    EVOLVE_SPEC_V2_SCHEMA = {}

LLM_PATCH_V1_SCHEMA = json.loads(
    res.files(__package__)
    .joinpath("llm_patch.schema.v1.json")
    .read_text(encoding="utf-8")
)


# ── EXTRAS schemas ─────────────────────────────────────────────
_extras_pkg = res.files(__package__).joinpath("extras")
EXTRAS_SCHEMAS = {
    fp.name.replace(".schema.v1.json", ""): json.loads(fp.read_text(encoding="utf-8"))
    for fp in _extras_pkg.iterdir()
    if fp.name.endswith(".schema.v1.json")
}

__all__ = [
    "PEAGEN_TOML_V1_SCHEMA",
    "PEAGEN_TOML_V1_1_SCHEMA",
    "DOE_SPEC_V1_SCHEMA",
    "DOE_SPEC_V1_1_SCHEMA",
    "DOE_SPEC_V2_SCHEMA",
    "PTREE_V1_SCHEMA",
    "PROJECTS_PAYLOAD_V1_SCHEMA",
    "EVENT_V1_SCHEMA",
    "EVOLVE_SPEC_V1_SCHEMA",
    "EVOLVE_SPEC_V2_SCHEMA",
    "LLM_PATCH_V1_SCHEMA",
    "EXTRAS_SCHEMAS",
]
