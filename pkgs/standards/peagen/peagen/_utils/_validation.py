"""Utility helpers for jsonschema validation."""

from __future__ import annotations

from jsonschema import Draft7Validator
import typer


def _path(err) -> str:
    """Return dotted-path to a failing node."""
    return ".".join(str(p) for p in err.absolute_path) or "(root)"


def _print_errors(errors) -> None:
    """Emit formatted jsonschema error messages."""
    for err in errors:
        typer.echo(f"   • {_path(err)} – {err.message}", err=True)
        for sub in err.context:
            typer.echo(f"     ↳ {_path(sub)} – {sub.message}", err=True)


def _validate(data: dict, schema: dict, label: str) -> None:
    """Run Draft7 validation and pretty-print errors."""
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        typer.echo(f"❌  Invalid {label}:", err=True)
        _print_errors(errors)
        raise typer.Exit(1)
    typer.echo(f"✅  {label.capitalize()} is valid.")
