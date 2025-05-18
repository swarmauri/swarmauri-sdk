# peagen/commands/doe.py
"""
Peagen “doe” sub-command – split out from cli.py.

Usage (wired in peagen/cli.py):
    from peagen.commands.doe import doe_app
    app.add_typer(doe_app, name="doe")
"""

import typer

# ── absolute-import everything ────────────────────────────────────────────────
from peagen.doe import DOEManager

# ── Typer sub-app boilerplate ─────────────────────────────────────────────────
doe_app = typer.Typer(help="Generate project payloads via a DOE spec and base template.")

@doe_app.command("doe")
def doe_generate(
    spec: str = typer.Argument(..., help="Path to the DOE spec YAML file."),
    template: str = typer.Argument(..., help="Path to the template_project.yaml file."),
    output: str = typer.Option(
        "project_payloads.yaml",
        "--output", "-o",
        help="Output path for the generated DOE payloads YAML."
    ),
):
    """
    Generate project payloads via a DOE spec and base template.
    """
    from .doe import DOEManager

    mgr = DOEManager(spec_path=spec, template_path=template)
    payloads = mgr.generate()
    mgr.write_payloads(output)

    typer.echo(
        f"DOE generation complete: {len(payloads)} experiments written to {output}"
    )