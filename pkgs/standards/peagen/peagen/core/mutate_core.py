"""
peagen.core.mutate_core
───────────────────────
Minimal GA-style optimisation of a single Python file *inside a task
work-tree*.

Key updates
-----------
* **Work-tree first** – clone/fetch logic replaced with mirror + `add_git_worktree`,
  protected by `repo_lock`.
* **No storage adapters** – artefacts are written directly into the work-tree.
* **No `workspace_uri` fallback** – caller must supply `repo` **and** `ref`.
"""

from __future__ import annotations

import hashlib
import logging
import random
import textwrap
import uuid
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from peagen._utils.config_loader import resolve_cfg
from peagen.plugin_manager import PluginManager, resolve_plugin_spec
from peagen.core.git_repo_core import (
    repo_lock,
    open_repo,
    fetch_git_remote,
)
from peagen.core.git_repo_core import (
    add_git_worktree,
)  # imported separately for clarity
from peagen.defaults import ROOT_DIR
from swarmauri_standard.programs.Program import Program

# ────────────────────────────── prompt  ───────────────────────────────
PROMPT = """\
Improve the python code below. Return only the new version.
```python
{parent}
```"""


# ─────────────────────────── mutator helper  ──────────────────────────
def _pick_mutators(
    pm: PluginManager,
    mutations: Optional[List[Dict[str, Any]]] = None,
) -> List[Tuple[float, Any]]:
    """Return list of (probability, mutator-instance)."""
    if not mutations:
        return [(1.0, pm.get("mutators"))]

    chosen: List[Tuple[float, Any]] = []
    for spec in mutations:
        prob = float(spec.get("probability", 1))
        kind = spec.get("kind")
        params = {k: v for k, v in spec.items() if k not in {"kind", "probability"}}
        MutCls = resolve_plugin_spec("mutators", kind)
        chosen.append((prob, MutCls(**params)))
    return chosen


# ───────────────────────────── public API  ────────────────────────────
def mutate_workspace(  # noqa: PLR0913
    *,
    repo: str,
    ref: str = "HEAD",
    target_file: str,
    import_path: str,
    entry_fn: str,
    gens: int = 1,
    profile_mod: str | None = None,
    cfg_path: Optional[Path] = None,
    mutations: Optional[List[Dict[str, Any]]] = None,
    evaluator_ref: str = "performance_evaluator",
) -> Dict[str, Optional[str]]:
    """
    Evolve *target_file* within an isolated work-tree and return the winner.

    Returns
    -------
    dict  –  {
        "winner": <abs-path>,
        "score": <float|None>,
        "meta":  <dict|None>,
        "worktree": <path to work-tree>
    }
    """
    # ── 1. Create / refresh mirror & work-tree ─────────────────────────
    repo_hash = hashlib.sha1(repo.encode()).hexdigest()[:12]
    mirror_base = Path(ROOT_DIR).expanduser() / "mirrors"
    mirror_path = mirror_base / repo_hash

    worktree_base = Path(ROOT_DIR).expanduser() / "worktrees"
    worktree_path = (
        worktree_base
        / repo_hash
        / ref.replace("/", "_")
        / f"mutate_{uuid.uuid4().hex[:8]}"
    )

    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    with repo_lock(repo):
        git_repo = open_repo(mirror_path, remote_url=repo)
        fetch_git_remote(git_repo)
        add_git_worktree(git_repo, ref, worktree_path)

    # ── 2. Config & plugin manager ─────────────────────────────────────
    cfg_file = cfg_path or worktree_path / ".peagen.toml"
    cfg = resolve_cfg(toml_path=str(cfg_file)) if cfg_file.exists() else {}
    pm = PluginManager(cfg)

    # mutators & evaluator
    mutators = _pick_mutators(pm, mutations)
    pool = pm.get("evaluator_pools")
    EvalCls = resolve_plugin_spec("evaluators", evaluator_ref)
    evaluator = EvalCls(
        import_path=import_path, entry_fn=entry_fn, profile_mod=profile_mod
    )
    pool.add_evaluator(evaluator, name="performance")

    # ── 3. GA loop ─────────────────────────────────────────────────────
    tgt_path = worktree_path / target_file
    parent_src = tgt_path.read_text(encoding="utf-8")
    program = Program.from_workspace(worktree_path)

    best_src, best_score, best_meta = parent_src, float("inf"), None
    weights, muts = zip(*mutators)

    for _ in range(max(1, gens)):
        prompt = textwrap.dedent(PROMPT.format(parent=best_src))
        mutator = random.choices(muts, weights=weights, k=1)[0]

        with suppress(Exception):
            child_src = mutator.mutate(prompt)
        if "child_src" not in locals():
            logging.warning("mutator failed; keeping parent source")
            child_src = best_src

        program.content[target_file] = child_src
        try:
            score, meta = evaluator.evaluate(program)
        except Exception as exc:  # noqa: BLE001
            logging.warning("evaluation error: %s", exc)
            score, meta = float("inf"), {}

        if score < best_score:
            best_src, best_score, best_meta = child_src, score, meta

    winner_path = worktree_path / "winner.py"
    winner_path.write_text(best_src, encoding="utf-8")

    return {
        "winner": str(winner_path),
        "score": str(best_score) if best_score != float("inf") else None,
        "meta": best_meta,
        "worktree": str(worktree_path),
    }
