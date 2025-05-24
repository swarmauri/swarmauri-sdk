# jaml/_comprehension.py
from __future__ import annotations
from typing import Iterator, Any
import re

import logging

logger = logging.getLogger(__name__)  # put this with your other imports
logger.setLevel(logging.DEBUG)  # caller can override


logger.debug("[_comprehension] module loaded")


# ④ evaluate list- and dict-comprehension strings
list_comp_pattern = re.compile(r"^\s*\[.*\bfor\b.*\]\s*$")
dict_comp_pattern = re.compile(r"^\s*\{.*\bfor\b.*\}\s*$")


def _eval_comprehensions(obj: Any) -> Any:
    logger.debug(f"[_eval_comprehensions] entering: obj={obj}")
    if isinstance(obj, dict):
        return {k: _eval_comprehensions(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_eval_comprehensions(v) for v in obj]
    if isinstance(obj, str):
        if list_comp_pattern.match(obj):
            try:
                return eval(obj)
            except Exception:
                return obj
        if dict_comp_pattern.match(obj):
            python_syntax = re.sub(r"=(?=[^}]*\bfor\b)", ":", obj)
            try:
                # THIS DOES NOT USE THE SAFE_EVAL METHOD
                # CAUTION SHOULD BE EXERCISED UNTIL PATCHED.
                return eval(python_syntax)
            except Exception:
                return obj
    return obj


def _evaluate_comprehension(node, global_env, context=None):
    from ._ast_nodes import ListComprehensionNode

    logger.debug(
        f"[_evaluate_comprehension] entering: node={node}, global_env_keys={list(global_env.keys())}, context={context}"
    )
    results = []
    for env in iter_environments(node.clauses, global_env, {}, context or {}):
        logger.debug(f"[_evaluate_comprehension] iteration env={env}")
        # resolve header_expr (for lists) or pair (for dicts)
        if hasattr(node, "header_expr"):
            logger.debug(
                f"[_evaluate_comprehension] resolving header_expr: {node.header_expr}"
            )
            node.header_expr.resolve(global_env, env)
            logger.debug(
                f"[_evaluate_comprehension] resolved header_expr.resolved={node.header_expr.resolved}"
            )
            results.append(node.header_expr.resolved)
        else:
            logger.debug(f"[_evaluate_comprehension] resolving pair: {node.pair}")
            node.pair.resolve(global_env, env)
            k, v = node.pair.resolved
            logger.debug(
                f"[_evaluate_comprehension] resolved pair -> key={k}, value={v}"
            )
            results.append((k, v))
    # for dict comprehensions, you’d turn results into a dict
    if isinstance(node, ListComprehensionNode):
        logger.debug(
            f"[_evaluate_comprehension] returning list of length {len(results)}"
        )
        return results
    else:
        result_dict = dict(results)
        logger.debug(
            f"[_evaluate_comprehension] returning dict of size {len(result_dict)}"
        )
        return result_dict


# ────────────────────────────────────────────────────────────────
# _comprehension.py · function iter_environments                 │
# ────────────────────────────────────────────────────────────────


def iter_environments(clauses, global_env, local_env, context) -> Iterator[dict]:
    from ._ast_nodes import AliasClauseNode, BaseNode

    clause_list = clauses.clauses

    def _rec(idx: int, env: dict):
        logger.debug(f"{idx} {env}")
        if idx == len(clause_list):
            yield env
            return

        clause = clause_list[idx]
        iterable = clause.iterable

        # evaluate the iterable -------------------------------------------------
        if (
            context is not None
            and hasattr(iterable, "render")
            and type(iterable).render is not BaseNode.render
        ):
            iterable_vals = iterable.render(global_env, {**local_env, **env}, context)
        else:
            if hasattr(iterable, "resolve"):
                iterable.resolve(global_env, {**local_env, **env})
                iterable_vals = iterable.resolved
            else:
                iterable_vals = iterable
        iterable_vals = iterable_vals or []

        # main loop -------------------------------------------------------------
        logger.debug(f"iterable_vals: {iterable_vals}")
        for item in iterable_vals:
            new_env = dict(env)
            bound_any = False

            for var in getattr(clause, "loop_vars", []):
                bound_any = True
                if isinstance(var, AliasClauseNode):
                    alias_name = var.resolve(global_env, new_env)  # ✔ fixed
                    new_env[alias_name] = item
                else:
                    name = getattr(var, "value", str(var))
                    new_env[name] = item

            if not bound_any:
                continue

            # conditions --------------------------------------------------------
            passed = True
            for cond in getattr(clause, "conditions", []):
                cond_val = (
                    cond.render(global_env, new_env, context)
                    if hasattr(cond, "render") and context
                    else (cond.resolve(global_env, new_env) or cond.evaluate())
                )
                if not cond_val:
                    passed = False
                    break
            if not passed:
                continue

            yield from _rec(idx + 1, new_env)

    yield from _rec(0, {})
