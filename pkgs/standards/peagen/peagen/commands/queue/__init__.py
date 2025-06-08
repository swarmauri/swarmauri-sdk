from __future__ import annotations

import typer

from .dlq import dlq_app

queue_app = typer.Typer(help="Queue utilities")
queue_app.add_typer(dlq_app, name="dlq")

__all__ = ["queue_app"]
