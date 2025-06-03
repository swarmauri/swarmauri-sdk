# peagen/commands/validate.py
"""Validate manifests and configuration files."""

from __future__ import annotations

import json
from pathlib import Path
import typer
import yaml
from swarmauri_standard.loggers.Logger import Logger
from peagen._utils._validation import _validate

# ── central schema registry ─────────────────────────────────────────────
from peagen.schemas import (
    PEAGEN_TOML_V1_SCHEMA,
    DOE_SPEC_V1_SCHEMA,
    MANIFEST_V3_SCHEMA,
    PTREE_V1_SCHEMA,  # ← new
    PROJECTS_PAYLOAD_V1_SCHEMA,  # ← new
)

from peagen._utils.config_loader import load_peagen_toml

validate_app = typer.Typer(help="Validation utilities for Peagen artefacts.")



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
    self = Logger(name="validate_config")
    self.logger.info("Entering validate_config command")
    cfg = load_peagen_toml(path.parent if path else Path.cwd())
    if not cfg:
        typer.echo("❌  No .peagen.toml found.", err=True)
        raise typer.Exit(1)
    _validate(cfg, PEAGEN_TOML_V1_SCHEMA, ".peagen.toml")
    self.logger.info("Exiting validate_config command")


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
    self = Logger(name="validate_doe_spec")
    self.logger.info("Entering validate_doe_spec command")
    try:
        with spec_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        typer.echo(f"❌  YAML parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(data, DOE_SPEC_V1_SCHEMA, "DOE spec")
    self.logger.info("Exiting validate_doe_spec command")


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
    self = Logger(name="validate_manifest")
    self.logger.info("Entering validate_manifest command")
    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        typer.echo(f"❌  JSON parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(data, MANIFEST_V3_SCHEMA, "manifest")
    self.logger.info("Exiting validate_manifest command")


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
    self = Logger(name="validate_ptree")
    self.logger.info("Entering validate_ptree command")
    try:
        with ptree_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        typer.echo(f"❌  YAML parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(
        data, PTREE_V1_SCHEMA, "ptree"
    )  # schema file :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
    self.logger.info("Exiting validate_ptree command")


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
    self = Logger(name="validate_projects_payload")
    self.logger.info("Entering validate_projects_payload command")
    try:
        with payload_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        typer.echo(f"❌  YAML parsing error – {exc}", err=True)
        raise typer.Exit(1)
    _validate(
        data, PROJECTS_PAYLOAD_V1_SCHEMA, "projects-payload"
    )  # schema file :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
    self.logger.info("Exiting validate_projects_payload command")
