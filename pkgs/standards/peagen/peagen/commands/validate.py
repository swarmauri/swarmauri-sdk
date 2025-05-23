# peagen/commands/validate.py
"""Validate manifests and configuration files."""

from __future__ import annotations

import json
from pathlib import Path
import typer
import yaml
from jsonschema import Draft7Validator

# ── central schema registry ─────────────────────────────────────────────
from peagen.schemas import (
    PEAGEN_TOML_V1_SCHEMA,
    DOE_SPEC_V1_SCHEMA,
    MANIFEST_V3_SCHEMA,
    PTREE_V1_SCHEMA,  # ← new
    PROJECTS_PAYLOAD_V1_SCHEMA,  # ← new
)

from peagen.cli_common import load_peagen_toml

validate_app = typer.Typer(help="Validation utilities for Peagen artefacts.")


# ─────────────────────────────────────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────────────────────────────────────
def _path(err) -> str:
    """Return dotted-path to failing node.
    File: **validate.py** • Method: **_path**"""
    return ".".join(str(p) for p in err.absolute_path) or "(root)"


def _print_errors(errors) -> None:
    """Emit every jsonschema error.
    File: **validate.py** • Method: **_print_errors**"""
    for err in errors:
        typer.echo(f"   • {_path(err)} – {err.message}", err=True)
        for sub in err.context:
            typer.echo(f"     ↳ {_path(sub)} – {sub.message}", err=True)


def _validate(data: dict, schema: dict, label: str) -> None:
    """Run Draft7 validation and pretty-print errors.
    File: **validate.py** • Method: **_validate**"""
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        typer.echo(f"❌  Invalid {label}:", err=True)
        _print_errors(errors)
        raise typer.Exit(1)
    typer.echo(f"✅  {label.capitalize()} is valid.")


# ─────────────────────────────────────────────────────────────────────────────
#  .peagen.toml
# ─────────────────────────────────────────────────────────────────────────────
@validate_app.command("config")
def validate_config(
    ctx: typer.Context,
    path: Path = typer.Argument(
        None,
        exists=False,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Optional explicit path to a .peagen.toml (defaults to discovery).",
    ),
) -> None:
    """File: **validate.py** • Method: **validate_config**"""
    cfg = load_peagen_toml(path.parent if path else Path.cwd())
    if not cfg:
        typer.echo("❌  No .peagen.toml found.", err=True)
        raise typer.Exit(1)
    _validate(cfg, PEAGEN_TOML_V1_SCHEMA, ".peagen.toml")


# ─────────────────────────────────────────────────────────────────────────────
#  DOE spec YAML
# ─────────────────────────────────────────────────────────────────────────────
@validate_app.command("doe")
def validate_doe_spec(
    ctx: typer.Context,
    spec_path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to a DOE-spec YAML file.",
    ),
) -> None:
    """File: **validate.py** • Method: **validate_doe_spec**"""
    try:
        with spec_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        typer.echo(f"❌  YAML parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(data, DOE_SPEC_V1_SCHEMA, "DOE spec")


# ─────────────────────────────────────────────────────────────────────────────
#  Manifest JSON
# ─────────────────────────────────────────────────────────────────────────────
@validate_app.command("manifest")
def validate_manifest(
    ctx: typer.Context,
    manifest_path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to a Peagen manifest JSON file.",
    ),
) -> None:
    """File: **validate.py** • Method: **validate_manifest**"""
    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        typer.echo(f"❌  JSON parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(data, MANIFEST_V3_SCHEMA, "manifest")


# ─────────────────────────────────────────────────────────────────────────────
#  Ptree YAML
# ─────────────────────────────────────────────────────────────────────────────
@validate_app.command("ptree")
def validate_ptree(
    ctx: typer.Context,
    ptree_path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to a ptree.yaml file.",
    ),
) -> None:
    """File: **validate.py** • Method: **validate_ptree**"""
    try:
        with ptree_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        typer.echo(f"❌  YAML parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(
        data, PTREE_V1_SCHEMA, "ptree"
    )  # schema file :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}


# ─────────────────────────────────────────────────────────────────────────────
#  Projects-payload YAML
# ─────────────────────────────────────────────────────────────────────────────
@validate_app.command("projects_payload")
def validate_projects_payload(
    ctx: typer.Context,
    payload_path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to a projects_payload.yaml file.",
    ),
) -> None:
    """File: **validate.py** • Method: **validate_projects_payload**"""
    try:
        with payload_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        typer.echo(f"❌  YAML parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(
        data, PROJECTS_PAYLOAD_V1_SCHEMA, "projects-payload"
    )  # schema file :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
