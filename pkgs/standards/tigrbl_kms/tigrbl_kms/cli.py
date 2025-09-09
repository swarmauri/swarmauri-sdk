#!/usr/bin/env python3
"""Entry point for the TigrblKMS command-line interface."""

from __future__ import annotations

import typer
import uvicorn


app = typer.Typer(help="CLI for TigrblKMS service")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(True, help="Auto-reload on changes"),
):
    """Start the TigrblKMS FastAPI service via uvicorn."""
    uvicorn.run(
        "tigrbl_kms.app:app",
        host=host,
        port=port,
        reload=reload,
        factory=False,
    )


if __name__ == "__main__":
    app()
