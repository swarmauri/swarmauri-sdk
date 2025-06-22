import asyncio
import textwrap
import uuid
from pathlib import Path
from typing import Any, Dict

import typer

from peagen.handlers.init_handler import init_handler
from peagen.models.schemas import Task
from peagen.plugins import discover_and_register_plugins


def _call_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke ``init_handler`` synchronously."""
    # Ensure plugin templates are registered before invoking handlers
    discover_and_register_plugins()
    task = Task(
        id=str(uuid.uuid4()),
        pool="default",
        payload={"action": "init", "args": args},
    )
    return asyncio.run(init_handler(task))


def _submit_task(args: Dict[str, Any], gateway_url: str, tag: str) -> None:
    """Send *args* to a JSON-RPC worker."""
    task = Task(
        id=str(uuid.uuid4()), pool="default", payload={"action": "init", "args": args}
    )
    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {
            "pool": task.pool,
            "payload": task.payload,
            "taskId": task.id,
        },
    }

    try:
        import httpx

        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted {tag} → taskId={data['result']['taskId']}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(f"""\
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """)
    )
