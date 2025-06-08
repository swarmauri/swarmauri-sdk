from __future__ import annotations

import typer

from peagen.cli_common import global_cli_options

mutate_app = typer.Typer(help="Mutate source with LLM")


def run_mutate(
    target_file: str,
    entry_fn: str,
    output: str,
    backend: str | None,
    queue: bool,
) -> None:
    """Placeholder implementation for mutate workflow."""
    typer.echo(
        f"mutate target={target_file} entry={entry_fn} output={output} backend={backend} queue={queue}"
    )


@mutate_app.command("mutate")
@global_cli_options
def mutate_cmd(
    ctx: typer.Context,
    target_file: str = typer.Option(..., "--target-file", help="Source file"),
    entry_fn: str = typer.Option(..., "--entry-fn", help="Entry function"),
    output: str = typer.Option("target_mutated.py", "--output", help="Output file"),
    backend: str | None = typer.Option(None, "--backend", help="LLM backend"),
    queue: bool = typer.Option(True, "--queue/--sync", help="Queue tasks"),
) -> None:
    run_mutate(target_file, entry_fn, output, backend, queue)
