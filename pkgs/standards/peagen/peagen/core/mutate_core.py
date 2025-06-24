"""Simplified mutation workflow built on the peagen framework."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
import random

from peagen._utils.config_loader import resolve_cfg
from peagen.plugin_manager import PluginManager, resolve_plugin_spec
from swarmauri_standard.programs.Program import Program
import logging

PROMPT = """\
Improve the python code below. Return only the new version.
```python
{parent}
```"""


def mutate_workspace(
    *,
    workspace_uri: str,
    target_file: str,
    import_path: str,
    entry_fn: str,
    gens: int = 1,
    profile_mod: str | None = None,
    cfg_path: Optional[Path] = None,
    mutations: Optional[List[Dict[str, Any]]] = None,
    evaluator_ref: str = (
        "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator"
    ),
) -> Dict[str, Optional[str]]:
    """Run a minimal evolutionary loop on ``target_file`` inside ``workspace_uri``."""

    cfg = resolve_cfg(toml_path=str(cfg_path or Path(workspace_uri) / ".peagen.toml"))
    pm = PluginManager(cfg)
    if mutations:
        mutators: List[Tuple[float, Any]] = []
        for spec in mutations:
            prob = float(spec.get("probability", 1))
            kind = spec.get("kind")
            params = {k: v for k, v in spec.items() if k not in {"kind", "probability"}}
            MutCls = resolve_plugin_spec("mutators", kind)
            mutators.append((prob, MutCls(**params)))
    else:
        mutators = [(1.0, pm.get("mutators"))]
    pool = pm.get("evaluator_pools")
    eval_cls = resolve_plugin_spec("evaluators", evaluator_ref)
    evaluator = eval_cls(
        import_path=import_path, entry_fn=entry_fn, profile_mod=profile_mod
    )
    pool.add_evaluator(evaluator, name="performance")

    path = Path(workspace_uri) / target_file
    parent_src = path.read_text(encoding="utf-8")
    program = Program.from_workspace(Path(workspace_uri))

    best_src = parent_src
    best_score = float("inf")
    best_meta: Dict[str, Any] | None = None

    weights, muts = zip(*mutators)
    for _ in range(gens):
        prompt = textwrap.dedent(PROMPT.format(parent=best_src))
        chosen = random.choices(muts, weights=weights, k=1)[0]
        try:
            child_src = chosen.mutate(prompt)
        except Exception as e:
            logging.warning("mutate error: %s", e)
            child_src = best_src
        program.content[target_file] = child_src
        try:
            score, meta = evaluator.evaluate(program)
        except Exception as e:
            logging.warning("evaluation error: %s", e)
            score = float("inf")
            meta = {}
        if score < best_score:
            best_score = score
            best_src = child_src
            best_meta = meta

    out_path = Path(workspace_uri) / "winner.py"
    out_path.write_text(best_src, encoding="utf-8")
    return {"winner": str(out_path), "score": str(best_score), "meta": best_meta}
