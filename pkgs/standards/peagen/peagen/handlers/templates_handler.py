"""
Async entry-point for template-set management.

Input : TaskRead  – AutoAPI schema bound to the Task ORM table
Output: dict      – JSON-serialisable result from templates_core helpers
"""

from __future__ import annotations

from typing import Any, Dict

from autoapi.v3 import get_schema
from peagen.orm import Task

from peagen._utils import maybe_clone_repo
from peagen.core.templates_core import (
    list_template_sets,
    show_template_set,
    add_template_set,
    remove_template_set,
)

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")  # incoming model


# ─────────────────────────── main coroutine ───────────────────────────
async def templates_handler(task: TaskRead) -> Dict[str, Any]:
    """
    task.args MUST contain:

        {
            "action":  "list" | "show" | "add" | "remove",
            # list   → {}
            # show   → { "name": "<set-name>" }
            # add    → { "source": "<uri>", "from_bundle": "...",
            #             "editable": false, "force": false }
            # remove → { "name": "<set-name>" }
            "repo": "<git-url>",   # optional – for remote ops
            "ref" : "HEAD"         # optional – defaults to HEAD
        }
    """
    args: Dict[str, Any] = task.args or {}
    action: str | None = args.get("action")
    if action is None:
        raise ValueError("templates_handler: missing 'action' in task.args")

    repo_url = args.get("repo")
    ref = args.get("ref", "HEAD")

    # Clone repo (if provided) for template-set operations that require a VCS tree
    with maybe_clone_repo(repo_url, ref):
        if action == "list":
            return list_template_sets()

        if action == "show":
            return show_template_set(args["name"])

        if action == "add":
            return add_template_set(
                args["source"],
                from_bundle=args.get("from_bundle"),
                editable=args.get("editable", False),
                force=args.get("force", False),
            )

        if action == "remove":
            return remove_template_set(args["name"])

    raise ValueError(f"Unknown template-set operation '{action}'")
