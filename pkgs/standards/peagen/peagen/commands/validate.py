# peagen/commands/validate.py
from __future__ import annotations

from pathlib import Path
import typer
from jsonschema import Draft7Validator

from peagen.schemas import PEAGEN_TOML_V1_SCHEMA            # schema constant
from peagen.cli_common import load_peagen_toml              # helper that finds .peagen.toml

validate_app = typer.Typer(help="Validate a .peagen.toml file against the built-in schema.")


def _format_path(error) -> str:
    """
    File: **validate.py**
    Class: —
    Method: **_format_path**

    Return a dotted-path string to the failing node or '(root)'.
    """
    return ".".join(str(p) for p in error.absolute_path) or "(root)"


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

    Load the TOML configuration (explicit *path* or automatic discovery) and
    emit **all** schema violations with their dotted JSON-Pointer locations.
    Exits 0 on success, 1 on failure for CI pipelines.
    """
    cfg = load_peagen_toml(path.parent if path else Path.cwd())

    if not cfg:
        typer.echo("❌  No .peagen.toml found.", err=True)
        raise typer.Exit(code=1)

    validator = Draft7Validator(PEAGEN_TOML_V1_SCHEMA)
    errors = sorted(validator.iter_errors(cfg), key=lambda e: e.path)

    if errors:
        typer.echo("❌  Invalid configuration:", err=True)
        for err in errors:
            typer.echo(f"   • {_format_path(err)} – {err.message}", err=True)
            # Show nested errors (e.g. within oneOf/anyOf)
            for sub in err.context:
                typer.echo(f"     ↳ {_format_path(sub)} – {sub.message}", err=True)
        raise typer.Exit(code=1)

    typer.echo("✅  Configuration is valid.")
