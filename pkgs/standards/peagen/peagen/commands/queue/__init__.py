from __future__ import annotations

import typer

from .dlq import dlq_app
from .recover import recover_app

queue_app = typer.Typer(help="Queue utilities")
queue_app.add_typer(dlq_app, name="dlq")
queue_app.add_typer(recover_app, name="recover")

__all__ = ["queue_app"]
