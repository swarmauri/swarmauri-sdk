#!/usr/bin/env python3
"""Generate JSON Schemas for template-set EXTRAS sections."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List
import argparse

TEMPLATES_ROOT = Path("pkgs/standards/peagen/peagen/templates")
SCHEMAS_DIR = Path("pkgs/standards/peagen/peagen/schemas/extras")


def _parse_keys(md_path: Path) -> List[str]:
    """Return bullet list keys from an EXTRAS.md file."""
    keys: List[str] = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            key = line[2:].strip()
            if key:
                keys.append(key)
    return keys


def _build_schema(keys: List[str], set_name: str) -> dict:
    """Return JSON schema dict for given keys."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"https://example.com/extras/{set_name}.schema.json",
        "title": f"EXTRAS Schema for {set_name}",
        "type": "object",
        "properties": {k: {} for k in keys},
        "additionalProperties": False,
    }


def generate_schemas(templates_root: Path = TEMPLATES_ROOT) -> None:
    """Generate schema files for all template-sets."""
    SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
    for md_file in templates_root.glob("*/EXTRAS.md"):
        set_name = md_file.parent.name
        keys = _parse_keys(md_file)
        schema = _build_schema(keys, set_name)
        out_path = SCHEMAS_DIR / f"{set_name}.schema.v1.json"
        out_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
        template_out_path = md_file.parent / "extras.schema.v1.json"
        template_out_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
        print(f"✅ Wrote {out_path} and {template_out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate EXTRAS schemas")
    parser.add_argument(
        "--templates-root",
        type=Path,
        default=TEMPLATES_ROOT,
        help="Root directory containing template sets",
    )
    args = parser.parse_args()
    generate_schemas(args.templates_root)
