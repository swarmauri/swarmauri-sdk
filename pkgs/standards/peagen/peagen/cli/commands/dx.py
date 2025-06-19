from __future__ import annotations

from pathlib import Path

import typer

from peagen._utils.git_filter import add_filter, init_git_filter

local_dx_app = typer.Typer(help="Developer convenience commands.")


@local_dx_app.command("filter")
def local_dx_filter(
    uri: str | None = None,
    name: str = "default",
    config: Path = Path(".peagen.toml"),
    repo: Path = Path("."),
) -> None:
    """Configure *repo* to use a git filter.

    If *uri* is omitted, the default ``s3://peagen`` filter is used.
    """
    add_filter(uri, name=name, config=config)
    init_git_filter(repo, uri, name=name)
    typer.echo(f"Configured filter '{name}' -> {uri or 's3://peagen'}")
