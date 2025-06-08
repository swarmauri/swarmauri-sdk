from __future__ import annotations

import typer

from peagen.cli_common import global_cli_options

dlq_app = typer.Typer(help="Dead-letter queue tools")


def dlq_retry(kind: str) -> None:
    """Placeholder retry implementation."""
    typer.echo(f"retry dlq kind={kind}")


@dlq_app.command("retry")
@global_cli_options
def retry_cmd(ctx: typer.Context, kind: str = typer.Option(..., "--kind")) -> None:
    dlq_retry(kind)
