#!/usr/bin/env python3
"""Entry point for the Peagen command line interface."""

import typer

from .commands import (
    init_app,
    process_app,
    sort_app,
    template_sets_app,
    doe_app,
    program_app,
    validate_app,
    extras_app,
    eval_app,
)

from ._banner import _print_banner
_print_banner()

app = typer.Typer(help="CLI tool for processing project files using Peagen.")

app.add_typer(init_app, name="init")
app.add_typer(doe_app, name="doe")
app.add_typer(process_app)
app.add_typer(program_app, name="program")
app.add_typer(sort_app)
app.add_typer(template_sets_app, name="template-set")
app.add_typer(extras_app, name="extras-schemas")
app.add_typer(validate_app, name="validate")
app.add_typer(eval_app)

if __name__ == "__main__":
    app()
