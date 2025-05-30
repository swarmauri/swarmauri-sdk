from __future__ import annotations

import typer

from peagen.cli_common import global_cli_options

evolve_app = typer.Typer(help="Evolution utilities")


def evolve_step(
    target_file: str | None,
    entry_fn: str | None,
    selector: str | None,
    mutator: str | None,
    backend: str | None,
    sync: bool,
) -> None:
    """Placeholder step implementation."""
    typer.echo(
        f"evolve step target={target_file} entry={entry_fn} selector={selector} mutator={mutator} backend={backend} sync={sync}"
    )


def evolve_run(
    generations: int | None,
    target_ms: float | None,
    checkpoint: str,
    resume: bool,
    dashboard: bool,
) -> None:
    """Placeholder run implementation."""
    typer.echo(
        f"evolve run gens={generations} target_ms={target_ms} checkpoint={checkpoint} resume={resume} dashboard={dashboard}"
    )


@evolve_app.command("step")
@global_cli_options
def step_cmd(
    ctx: typer.Context,
    target_file: str | None = typer.Option(None, "--target-file"),
    entry_fn: str | None = typer.Option(None, "--entry-fn"),
    selector: str | None = typer.Option(None, "--selector"),
    mutator: str | None = typer.Option(None, "--mutator"),
    backend: str | None = typer.Option(None, "--backend"),
    sync: bool = typer.Option(False, "--sync"),
) -> None:
    evolve_step(target_file, entry_fn, selector, mutator, backend, sync)


@evolve_app.command("run")
@global_cli_options
def run_cmd(
    ctx: typer.Context,
    generations: int | None = typer.Option(None, "--generations"),
    target_ms: float | None = typer.Option(None, "--target-ms"),
    checkpoint: str = typer.Option(
        ".peagen/evo_checkpoint.msgpack", "--checkpoint", help="Checkpoint file"
    ),
    resume: bool = typer.Option(False, "--resume"),
    dashboard: bool = typer.Option(False, "--dashboard"),
) -> None:
    evolve_run(generations, target_ms, checkpoint, resume, dashboard)
