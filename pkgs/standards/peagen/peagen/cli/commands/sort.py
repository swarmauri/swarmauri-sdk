# peagen/commands/sort.py

import asyncio
import typer
import uuid
from typing import Any, Dict

from peagen.handlers.sort_handler import sort_handler
from peagen.models import Task  # pydantic model
from peagen.models import Status  # ensure Status is available if needed

sort_app = typer.Typer()


@sort_app.command("run")
def run_sort(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    start_idx: int = typer.Option(0, help="Index to start sorting from."),
    start_file: str = typer.Option(None, help="File to start sorting from."),
    verbose: int = typer.Option(0, help="Verbosity level."),
    transitive: bool = typer.Option(False, help="Include transitive dependencies."),
    show_dependencies: bool = typer.Option(False, help="Show dependency info."),
):
    """
    Run sort locally (no queue) by constructing a Task model
    and invoking the same handler that a worker would use.
    """
    # 1) Create a Task instance with default status/result
    task_id = str(uuid.uuid4())
    args: Dict[str, Any] = {
        "projects_payload": projects_payload,
        "project_name": project_name,
        "start_idx": start_idx,
        "start_file": start_file,
        "verbose": verbose,
        "transitive": transitive,
        "show_dependencies": show_dependencies,
    }
    task = Task(
        id=task_id,
        pool="default",
        payload={"action": "sort", "args": args},
        # status and result left as defaults (Status.pending, None)
    )

    # 2) Call sort_handler with the Task instance via asyncio.run
    try:
        result: Dict[str, Any] = asyncio.run(sort_handler(task))
    except Exception as exc:
        typer.echo(f"[ERROR] Exception inside sort_handler: {exc}")
        raise typer.Exit(1)

    # 3) Inspect the returned dict
    if "error" in result:
        typer.echo(f"[ERROR] {result['error']}")
        raise typer.Exit(1)

    # 4) Print sorted output
    if "sorted" in result:
        for line in result["sorted"]:
            typer.echo(line)
    else:
        for proj, files in result.get("sorted_all_projects", {}).items():
            typer.echo(f"Project {proj}:")
            for line in files:
                typer.echo(f"  {line}")


@sort_app.command("submit")
def submit_sort(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    start_idx: int = typer.Option(0, help="Index to start sorting from."),
    start_file: str = typer.Option(None, help="File to start sorting from."),
    verbose: int = typer.Option(0, help="Verbosity level."),
    transitive: bool = typer.Option(False, help="Include transitive dependencies."),
    show_dependencies: bool = typer.Option(False, help="Show dependency info."),
    gateway_url: str = typer.Option(
        "http://localhost:8000/rpc", "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    """
    Submit this sort as a background task. Returns immediately with a taskId.
    """
    # 1) Create a Task instance
    task_id = str(uuid.uuid4())
    args: Dict[str, Any] = {
        "projects_payload": projects_payload,
        "project_name": project_name,
        "start_idx": start_idx,
        "start_file": start_file,
        "verbose": verbose,
        "transitive": transitive,
        "show_dependencies": show_dependencies,
    }
    task = Task(
        id=task_id,
        pool="default",
        payload={"action": "sort", "args": args},
        # status and result left as defaults
    )

    # 2) Build Work.start envelope using Task fields
    envelope = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "Work.start",
        "params": {
            "id": task.id,
            "pool": task.pool,
            "payload": task.payload,
        },
    }

    # 3) POST to gateway
    try:
        import httpx

        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted sort → taskId={task.id}")
    except Exception as exc:
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
