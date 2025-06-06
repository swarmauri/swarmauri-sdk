"""Utility functions for generating EXTRAS JSON schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


def parse_keys(md_path: Path) -> List[str]:
    """Return bullet list keys from an EXTRAS.md file."""
    keys: List[str] = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            key = line[2:].strip()
            if key:
                keys.append(key)
    return keys


def build_schema(keys: List[str], set_name: str) -> dict:
    """Return JSON schema dict for given keys."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"https://example.com/extras/{set_name}.schema.json",
        "title": f"EXTRAS Schema for {set_name}",
        "type": "object",
        "properties": {k: {} for k in keys},
        "additionalProperties": False,
    }


def generate_schemas(templates_root: Path, schemas_dir: Path) -> List[Path]:
    """Generate schema files for all EXTRAS templates.

    Parameters
    ----------
    templates_root : Path
        Directory containing template-set folders with ``EXTRAS.md`` files.
    schemas_dir : Path
        Destination directory for generated ``*.schema.v1.json`` files.

    Returns
    -------
    List[Path]
        Paths of all schema files written.
    """
    schemas_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for md_file in templates_root.glob("*/EXTRAS.md"):
        set_name = md_file.parent.name
        keys = parse_keys(md_file)
        schema = build_schema(keys, set_name)
        out_path = schemas_dir / f"{set_name}.schema.v1.json"
        out_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
        written.append(out_path)
    return written
