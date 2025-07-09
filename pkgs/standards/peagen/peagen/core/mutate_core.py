"""
peagen.core.mutate_core
───────────────────────
Light-weight “evolution” helper used by the *mutate* task handler.

The previous implementation expected a *workspace_uri* that could point to a
local directory *or* a git-style URI.  The new pipeline always supplies a
concrete git *repo* **and** a *ref* (branch / tag / SHA).  This module therefore

1. clones the requested revision into a disposable checkout;
2. runs a very small GA-style search over *target_file*;
3. returns the path of the winning variant plus basic telemetry.

No legacy fallback for *workspace_uri* remains.
"""

from __future__ import annotations

import logging
import random
import shutil
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from peagen._utils.config_loader import resolve_cfg
from peagen.plugin_manager import PluginManager, resolve_plugin_spec
from peagen.plugins.vcs import open_repo         # optional; may raise
from peagen.core.fetch_core import fetch_single  # shallow clone helper
from swarmauri_standard.programs.Program import Program

# --------------------------------------------------------------------- #
PROMPT = """\
Improve the python code below. Return only the new version.
```python
{parent}
```"""
# --------------------------------------------------------------------- #


def _pick_mutators(
    pm: PluginManager,
    mutations: Optional[List[Dict[str, Any]]] = None,
) -> List[Tuple[float, Any]]:
    """Return a list (probability, mutator-instance) from *mutations* spec."""
    if not mutations:
        return [(1.0, pm.get("mutators"))]  # default bundled mutator

    chosen: List[Tuple[float, Any]] = []
    for spec in mutations:
        prob = float(spec.get("probability", 1))
        kind = spec.get("kind")
        params = {k: v for k, v in spec.items() if k not in {"kind", "probability"}}
        MutCls = resolve_plugin_spec("mutators", kind)
        chosen.append((prob, MutCls(**params)))
    return chosen


# ───────────────────────────── public API ──────────────────────────────
def mutate_workspace(  # noqa: PLR0913 – many tunables by design
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
    evaluator_ref: str = (
        "performance_evaluator"
    ),
) -> Dict[str, Optional[str]]:
    """
    Run a very small GA-style search over *target_file* in *repo@ref*.

    Parameters
    ----------
    repo, ref
        Git repository URL (SSH / HTTPS / local path) and revision to check out.
    target_file
        File **relative to the repo root** to mutate.
    import_path, entry_fn
        Fully-qualified module import path and entry function for benchmarking.
    gens
        Number of generations (1 ⇒ parent + one child).
    profile_mod
        Optional helper module for the evaluator.
    cfg_path
        Path to an overriding *.peagen.toml* (rarely needed).
    mutations
        List of mutator specs – see documentation for exact schema.
    evaluator_ref
        Plugin reference resolving to an Evaluator subclass.

    Returns
    -------
    Dict[str, Optional[str]]
        { "winner": <abs-path>, "score": <float>, "meta": <dict> }
    """

    # ------------------------------------------------------------------ #
    # 1. clone requested revision into a temp dir
    # ------------------------------------------------------------------ #
    checkout_dir = Path(tempfile.mkdtemp(prefix="pea_mutate_"))
    try:
        fetch_single(repo=repo, ref=ref, dest_root=checkout_dir)
    except Exception as exc:
        shutil.rmtree(checkout_dir, ignore_errors=True)
        raise RuntimeError(f"clone failed: {exc}") from exc

    # workspace for downstream helpers
    workspace_root = checkout_dir
    cfg = resolve_cfg(toml_path=str(cfg_path or workspace_root / ".peagen.toml"))
    pm = PluginManager(cfg)

    # ------------------------------------------------------------------ #
    # 2. build mutator & evaluator pool
    # ------------------------------------------------------------------ #
    mutators = _pick_mutators(pm, mutations)

    pool = pm.get("evaluator_pools")
    EvalCls = resolve_plugin_spec("evaluators", evaluator_ref)
    evaluator = EvalCls(
        import_path=import_path,
        entry_fn=entry_fn,
        profile_mod=profile_mod,
    )
    pool.add_evaluator(evaluator, name="performance")

    # ------------------------------------------------------------------ #
    # 3. baseline source + GA loop
    # ------------------------------------------------------------------ #
    tgt_path = workspace_root / target_file
    parent_src = tgt_path.read_text(encoding="utf-8")
    program = Program.from_workspace(workspace_root)

    best_src = parent_src
    best_score = float("inf")
    best_meta: Dict[str, Any] | None = None

    weights, muts = zip(*mutators)
    for _ in range(max(1, gens)):
        prompt = textwrap.dedent(PROMPT.format(parent=best_src))
        mutator = random.choices(muts, weights=weights, k=1)[0]

        try:
            child_src = mutator.mutate(prompt)
        except Exception as exc:  # noqa: BLE001
            logging.warning("mutator error: %s", exc)
            child_src = best_src

        program.content[target_file] = child_src
        try:
            score, meta = evaluator.evaluate(program)
        except Exception as exc:  # noqa: BLE001
            logging.warning("evaluation error: %s", exc)
            score, meta = float("inf"), {}

        if score < best_score:
            best_src, best_score, best_meta = child_src, score, meta

    winner_path = workspace_root / "winner.py"
    winner_path.write_text(best_src, encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 4. return results (caller may decide to commit / push etc.)
    # ------------------------------------------------------------------ #
    return {
        "winner": str(winner_path),
        "score": str(best_score) if best_score != float("inf") else None,
        "meta": best_meta,
        "checkout_root": str(checkout_dir),
    }
