# peagen/commands/templates.py
"""
Peagen “templates” sub-command – split out from cli.py.

Usage (wired in peagen/cli.py):
    from peagen.commands.templates import templates_app
    app.add_typer(templates_app, name="templates")
"""

import typer
from pathlib import Path

# ── absolute-import everything ────────────────────────────────────────────────
import peagen.templates

# ── Typer sub-app boilerplate ─────────────────────────────────────────────────
templates_app = typer.Typer(help="List available template namespaces and folders.")

@templates_app.command("templates")
def get_templates(
    verbose: int = typer.Option(
        0, "-v", "--verbose", count=True, help="Verbosity level (-v, -vv, -vvv)"
    ),
):
    """
    Get template list.
    """
    import peagen.templates
    from pathlib import Path

    def detect_folders(path):
        try:
            directory = Path(path)
            if not directory.exists() or not directory.is_dir():
                return "Invalid or non-existent directory!"
            return [folder.name for folder in directory.iterdir() if folder.is_dir()]
        except PermissionError:
            return "Permission denied!"

    typer.echo("\nTemplate Directories:")
    namespace_dirs = list(peagen.templates.__path__)
    for _n in namespace_dirs:
        typer.echo(f"- {_n}")

    templates = []
    for each in [detect_folders(_n) for _n in namespace_dirs]:
        if isinstance(each, list):
            templates.extend(each)

    typer.echo("\nAvailable Template Folders:")
    for _t in templates:
        typer.echo(f"- {_t}")