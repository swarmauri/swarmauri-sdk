"""
Initialisation handler – delegates to peagen.core.init_core.*

Input : TaskRead  (AutoAPI schema for the Task table)
Output: dict      (serialisable result from init_core helpers)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi.v2 import get_schema
from peagen.orm import Task
from peagen.core import init_core

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")  # validated Pydantic model


# ─────────────────────────── main coroutine ───────────────────────────
async def init_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Dispatch to the appropriate *init_core* helper based on the ``kind``
    field found in **task.args**.
    """
    args: Dict[str, Any] = task.args or {}
    kind: str | None = args.get("kind")
    if not kind:
        raise ValueError("'kind' argument required")

    path = Path(args.get("path", ".")).expanduser()

    match kind:
        case "project":
            return init_core.init_project(
                path=path,
                force=args.get("force", False),
                git_remotes=args.get("git_remotes"),
                filter_uri=args.get("filter_uri"),
                add_filter_config=args.get("add_filter_config", False),
            )

        case "template-set":
            return init_core.init_template_set(
                path=path,
                name=args.get("name"),
                org=args.get("org"),
                use_uv=args.get("use_uv", True),
                force=args.get("force", False),
            )

        case "doe-spec":
            return init_core.init_doe_spec(
                path=path,
                name=args.get("name"),
                org=args.get("org"),
                force=args.get("force", False),
            )

        case "ci":
            return init_core.init_ci(
                path=path,
                github=args.get("github", True),
                force=args.get("force", False),
            )

        case "repo":
            return init_core.init_repo(
                repo=args.get("repo"),
                pat=args.get("pat"),
                description=args.get("description", ""),
                deploy_key=Path(args["deploy_key"]).expanduser()
                if args.get("deploy_key")
                else None,
                path=Path(args["path"]).expanduser() if args.get("path") else None,
                remotes=args.get("remotes"),
            )

        case "repo-config":
            return init_core.configure_repo(
                path=path,
                remotes=args.get("remotes", {}),
            )

    raise ValueError(f"Unknown init kind '{kind}'")
