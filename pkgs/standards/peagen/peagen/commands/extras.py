"""Generate extras schemas via CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import typer

extras_app = typer.Typer(help="Manage EXTRAS schemas.")


def _parse_keys(md_path: Path) -> List[str]:
    keys: List[str] = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            key = line[2:].strip()
            if key:
                keys.append(key)
    return keys


def _build_schema(keys: List[str], set_name: str) -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"https://example.com/extras/{set_name}.schema.json",
        "title": f"EXTRAS Schema for {set_name}",
        "type": "object",
        "properties": {k: {} for k in keys},
        "additionalProperties": False,
    }


@extras_app.command("generate")
def generate() -> None:
    """Regenerate EXTRAS schema files from templates."""
    base = Path(__file__).resolve().parents[1]
    templates_root = base / "templates"
    schemas_dir = base / "schemas" / "extras"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    for md_file in templates_root.glob("*/EXTRAS.md"):
        set_name = md_file.parent.name
        keys = _parse_keys(md_file)
        schema = _build_schema(keys, set_name)
        out_path = schemas_dir / f"{set_name}.schema.v1.json"
        out_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
        typer.echo(f"✅ Wrote {out_path}")
