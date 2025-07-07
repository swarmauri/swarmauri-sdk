# peagen/handlers/templates_handler.py
"""
Async entry-point for template-set management.

Input : TaskRead (AutoAPI schema bound to the Task ORM table)
Output: dict      (JSON-serialisable result from templates_core helpers)
"""

from __future__ import annotations

from typing import Any, Dict

from autoapi.v2          import AutoAPI
from peagen.orm          import Task

from peagen._utils                  import maybe_clone_repo
from peagen.core.templates_core     import (
    list_template_sets,
    show_template_set,
    add_template_set,
    remove_template_set,
)

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")                 # request model


# ─────────────────────────── main coroutine ───────────────────────────
async def templates_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected payload
    ----------------
    task.payload == {
        "action": "list" | "show" | "add" | "remove",
        "args":   {
            # list   → {}
            # show   → { "name": "<set-name>" }
            # add    → { "source": "<uri>", "from_bundle": "...", "editable": false,
            #             "force": false }
            # remove → { "name": "<set-name>" }
            "repo": "<git-url>",      # optional
            "ref" : "HEAD"            # optional, defaults to HEAD
        }
    }
    """
    payload: Dict[str, Any] = task.payload or {}
    action:  str | None     = payload.get("action")
    args:    Dict[str, Any] = payload.get("args", {})

    repo = args.get("repo")
    ref  = args.get("ref", "HEAD")

    with maybe_clone_repo(repo, ref):
        if action == "list":
            return list_template_sets()

        if action == "show":
            return show_template_set(args["name"])

        if action == "add":
            return add_template_set(
                args["source"],
                from_bundle = args.get("from_bundle"),
                editable    = args.get("editable", False),
                force       = args.get("force", False),
            )

        if action == "remove":
            return remove_template_set(args["name"])

    # If the code reaches here the action was unknown
    raise ValueError(f"Unknown template-set operation '{action}'")
