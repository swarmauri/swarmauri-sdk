# peagen/cli/commands/sort.py
"""
Sort generated project files locally or via the gateway.

Sub-commands
------------
• peagen sort run      – local, blocking
• peagen sort submit   – JSON-RPC submission
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

import typer

from peagen._utils.config_loader import _effective_cfg, load_peagen_toml
from peagen.handlers.sort_handler import sort_handler
from peagen.cli.task_helpers import build_task, submit_task, get_task
from peagen.orm import Status

from peagen.defaults import DEFAULT_POOL_ID

# ────────────────────────── apps ───────────────────────────────
local_sort_app = typer.Typer(help="Sort generated project files locally.")
remote_sort_app = typer.Typer(help="Submit sort tasks to the gateway.")


# ───────────────────── helper: build args dict ────────────────────────
def _base_args(
    projects_payload: str,
    project_name: Optional[str],
    start_idx: int,
    start_file: Optional[str],
    transitive: bool,
    show_dependencies: bool,
) -> Dict[str, Any]:
    return {
        "projects_payload": projects_payload,
        "project_name": project_name,
        "start_idx": start_idx,
        "start_file": start_file,
        "transitive": transitive,
        "show_dependencies": show_dependencies,
    }


# ─────────────────────────  LOCAL RUN  ────────────────────────────────
@local_sort_app.command("sort")
def run_sort(  # noqa: PLR0913
    ctx: typer.Context,
    projects_payload: str,
    project_name: Optional[str] = None,
    start_idx: int = 0,
    start_file: Optional[str] = None,
    transitive: bool = False,
    show_dependencies: bool = False,
    repo: Optional[str] = typer.Option(None, "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    # 1) config override
    cfg_path = ctx.obj.get("config_path") if ctx.obj else None
    cfg_override = _effective_cfg(cfg_path)

    # 2) build task
    args = _base_args(
        projects_payload,
        project_name,
        start_idx,
        start_file,
        transitive,
        show_dependencies,
    )
    if repo:
        args |= {"repo": repo, "ref": ref}
    args["cfg_override"] = cfg_override  # inject override

    task = build_task(
        action="sort",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    # 3) call handler
    try:
        result = asyncio.run(sort_handler(task))
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}", err=True)
        raise typer.Exit(1)

    # 4) output
    sorted_map = result.get("sorted_all_projects") or {"": result.get("sorted", [])}
    for proj, files in sorted_map.items():
        if proj:
            typer.echo(f"Project {proj}:")
        for line in files:
            typer.echo(("  " if proj else "") + line)


# ───────────────────────── REMOTE SUBMIT ──────────────────────────────
@remote_sort_app.command("sort")
def submit_sort(  # noqa: PLR0913
    ctx: typer.Context,
    projects_payload: str,
    project_name: Optional[str] = None,
    start_idx: int = 0,
    start_file: Optional[str] = None,
    transitive: bool = False,
    show_dependencies: bool = False,
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
    watch: bool = typer.Option(False, "--watch", "-w"),
    interval: float = typer.Option(2.0, "--interval", "-i"),
) -> None:
    # 1) read YAML text so workers need no local file access
    yaml_text = Path(projects_payload).read_text(encoding="utf-8")

    # 2) cfg_override from ctx
    inline = ctx.obj.get("task_override_inline")
    file_ = ctx.obj.get("task_override_file")
    cfg_override: Dict[str, Any] = {}
    if inline:
        cfg_override = json.loads(inline)
    if file_:
        cfg_override.update(load_peagen_toml(Path(file_), required=True))

    # 3) task args
    args = _base_args(
        yaml_text,
        project_name,
        start_idx,
        start_file,
        transitive,
        show_dependencies,
    ) | {"repo": repo, "ref": ref, "cfg_override": cfg_override}

    task = build_task(
        action="sort",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    # 4) submit via gateway
    resp = submit_task(ctx.obj["rpc"], task)
    if "error" in resp:
        typer.echo(f"[ERROR] {resp['error']['message']}", err=True)
        raise typer.Exit(1)

    tid = resp["id"]
    typer.echo(f"Submitted sort task {tid}")

    # optional watch
    if watch:
        while True:
            cur = get_task(ctx.obj["rpc"], tid)
            if Status.is_terminal(cur.status):
                break
            time.sleep(interval)
        typer.echo(json.dumps(cur.model_dump(), indent=2))
