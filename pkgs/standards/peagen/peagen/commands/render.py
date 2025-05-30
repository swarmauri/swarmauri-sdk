from __future__ import annotations

import pathlib
import typer

from peagen.cli_common import global_cli_options

render_app = typer.Typer(help="Render deterministic templates")


def run_render(project: str | None, out: str, queue: bool) -> None:
    """Placeholder implementation for render workflow."""
    # Real implementation would enqueue or run locally
    typer.echo(f"render project={project} out={out} queue={queue}")


@render_app.command("render")
@global_cli_options
def render_cmd(
    ctx: typer.Context,
    project: str | None = typer.Option(None, "--project", help="Project file"),
    out: str = typer.Option("./build", "--out", help="Output directory"),
    queue: bool = typer.Option(True, "--queue/--sync", help="Queue tasks"),
) -> None:
    run_render(project, out, queue)
