# peagen/commands/validate.py
from __future__ import annotations

from pathlib import Path
import typer
import yaml
from jsonschema import Draft7Validator

from peagen.schemas import (                 # ← gather both schema constants here
    PEAGEN_TOML_V1_SCHEMA,
    DOE_SPEC_V1_SCHEMA,
)
from peagen.cli_common import load_peagen_toml  # helper that finds .peagen.toml

validate_app = typer.Typer(help="Configuration and DOE-spec validation utilities.")


# ──────────────────────────────────────────────────────────────────────────────
#  Shared helpers
# ──────────────────────────────────────────────────────────────────────────────
def _format_path(error) -> str:
    """
    File: **validate.py**
    Class: —
    Method: **_format_path**

    Return a dotted-path string to the failing node or '(root)'.
    """
    return ".".join(str(p) for p in error.absolute_path) or "(root)"


def _dump_errors(errors) -> None:
    """
    File: **validate.py**
    Class: —
    Method: **_dump_errors**

    Emit all schema-validation errors in a readable list.
    """
    for err in errors:
        typer.echo(f"   • {_format_path(err)} – {err.message}", err=True)
        for sub in err.context:  # nested errors inside oneOf/anyOf/etc.
            typer.echo(f"     ↳ {_format_path(sub)} – {sub.message}", err=True)


# ──────────────────────────────────────────────────────────────────────────────
#  .peagen.toml validator
# ──────────────────────────────────────────────────────────────────────────────
@validate_app.command("config")
def validate_config(                                       # noqa: D401
    ctx: typer.Context,
    path: Path = typer.Argument(
        None,
        exists=False,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Optional explicit path to a .peagen.toml (defaults to auto-discovery).",
    ),
) -> None:
    """
    File: **validate.py**
    Class: —
    Method: **validate_config**

    Validate a Peagen **.peagen.toml** file against *PEAGEN_TOML_V1_SCHEMA* and
    list all schema violations with dotted paths.
    """
    cfg = load_peagen_toml(path.parent if path else Path.cwd())

    if not cfg:
        typer.echo("❌  No .peagen.toml found.", err=True)
        raise typer.Exit(code=1)

    validator = Draft7Validator(PEAGEN_TOML_V1_SCHEMA)
    errors = sorted(validator.iter_errors(cfg), key=lambda e: e.path)

    if errors:
        typer.echo("❌  Invalid configuration:", err=True)
        _dump_errors(errors)
        raise typer.Exit(code=1)

    typer.echo("✅  Configuration is valid.")


# ──────────────────────────────────────────────────────────────────────────────
#  DOE-spec YAML validator
# ──────────────────────────────────────────────────────────────────────────────
@validate_app.command("doe")
def validate_doe_spec(                                     # noqa: D401
    ctx: typer.Context,
    spec_path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to a DOE spec YAML file.",
    ),
) -> None:
    """
    File: **validate.py**
    Class: —
    Method: **validate_doe_spec**

    Validate a **DOE spec YAML** against *DOE_SPEC_V1_SCHEMA* with verbose
    error output.  Exits 0 on success, 1 on failure (CI-friendly).
    """
    try:
        with spec_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        typer.echo(f"❌  YAML parsing error – {exc}", err=True)
        raise typer.Exit(code=1)

    validator = Draft7Validator(DOE_SPEC_V1_SCHEMA)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if errors:
        typer.echo("❌  Invalid DOE spec:", err=True)
        _dump_errors(errors)
        raise typer.Exit(code=1)

    typer.echo("✅  DOE spec is valid.")
