"""Generate extras schemas via CLI."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict
from swarmauri_standard.loggers.Logger import Logger

import typer

from peagen.handlers.extras_handler import extras_handler
from peagen.models import Task

extras_app = typer.Typer(help="Manage EXTRAS schemas.")


@extras_app.command("generate")
def generate() -> None:
    """Regenerate EXTRAS schema files from templates."""
    self = Logger(name="extras_generate")
    self.logger.info("Entering extras_generate command")

    task = Task(id=str(uuid.uuid4()), pool="default", payload={"action": "extras", "args": {}})
    result: Dict[str, Any] = asyncio.run(extras_handler(task))

    for path in result.get("generated", []):
        typer.echo(f"✅ Wrote {path}")

    self.logger.info("Exiting extras_generate command")
