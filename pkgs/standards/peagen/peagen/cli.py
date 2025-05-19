#!/usr/bin/env python3
import typer

from peagen._banner import _print_banner
from peagen.commands import (
    init_app,
    process_app,
    revise_app,
    sort_app,
    template_sets_app,
    experiment_app,
)

_print_banner()

app = typer.Typer(help="CLI tool for processing project files using Peagen.")

app.add_typer(init_app, name="init")
app.add_typer(process_app)
app.add_typer(revise_app)
app.add_typer(sort_app)
app.add_typer(template_sets_app, name="template-set")
app.add_typer(experiment_app, name="doe")

if __name__ == "__main__":
    app()
