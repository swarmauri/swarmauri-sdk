"""Simplified mutation workflow built on the peagen framework."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Dict, Optional

from peagen._utils.config_loader import load_peagen_toml
from peagen.plugin_manager import PluginManager, resolve_plugin_spec
from swarmauri_standard.programs.Program import Program

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
) -> Dict[str, Optional[str]]:
    """Run a minimal evolutionary loop on ``target_file`` inside ``workspace_uri``."""

    cfg = load_peagen_toml(cfg_path) if cfg_path else load_peagen_toml(Path(workspace_uri) / ".peagen.toml")
    pm = PluginManager(cfg)
    mutator = pm.get("mutators")
    pool = pm.get("evaluator_pools")
    evaluator_ref = "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator"
    eval_cls = resolve_plugin_spec("evaluators", evaluator_ref)
    evaluator = eval_cls(import_path=import_path, entry_fn=entry_fn, profile_mod=profile_mod)
    pool.add_evaluator(evaluator, name="performance")

    path = Path(workspace_uri) / target_file
    parent_src = path.read_text(encoding="utf-8")
    program = Program.from_workspace(Path(workspace_uri))

    best_src = parent_src
    best_score = float("inf")

    for _ in range(gens):
        prompt = textwrap.dedent(PROMPT.format(parent=best_src))
        child_src = mutator.mutate(prompt)
        program.content[target_file] = child_src
        score, _ = evaluator.evaluate(program)
        if score < best_score:
            best_score = score
            best_src = child_src

    out_path = Path(workspace_uri) / "winner.py"
    out_path.write_text(best_src, encoding="utf-8")
    return {"winner": str(out_path), "score": str(best_score)}
