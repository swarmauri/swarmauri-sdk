# jaml/_comprehension.py
from __future__ import annotations
from typing import Dict, Iterator, Optional, Union, List
from ._eval import safe_eval

def _evaluate_comprehension(node, global_env, context=None):
    from ._ast_nodes import ListComprehensionNode
    results = []
    for env in iter_environments(node.clauses, global_env, {}, context or {}):
        # resolve header_expr (for lists) or pair (for dicts)
        if hasattr(node, 'header_expr'):
            node.header_expr.resolve(global_env, env)
            results.append(node.header_expr.resolved)
        else:
            node.pair.resolve(global_env, env)
            k, v = node.pair.resolved
            results.append((k, v))
    # for dict comprehensions, you’d turn results into a dict
    return results if isinstance(node, ListComprehensionNode) else dict(results)


def iter_environments(clauses, global_env, local_env, context):
    clause_list = clauses.clauses

    def _rec(idx, env):
        if idx == len(clause_list):
            yield env
            return

        clause = clause_list[idx]
        # Determine iterable values, resolving if necessary
        iterable = clause.iterable
        if hasattr(iterable, "resolve"):
            iterable.resolve(global_env, {**local_env, **env})
            iterable_vals = getattr(iterable, "resolved", []) or []
        else:
            iterable_vals = iterable or []

        for item in iterable_vals:
            new_env = {**env}

            # ── Bind loop variables ───────────────
            # Prefer the 'loop_vars' list (ComprehensionClauseNode)
            if hasattr(clause, "loop_vars") and clause.loop_vars:
                for var in clause.loop_vars:
                    name = getattr(var, "value", var)
                    new_env[name] = item
            # Fallback to a singular 'loop_var' (other comprehension types)
            elif hasattr(clause, "loop_var"):
                new_env[clause.loop_var.value] = item
            else:
                # No loop variable to bind: skip this branch
                continue

            # ── Apply any 'if' conditions ─────────
            passed = True
            for cond in getattr(clause, "conditions", []):
                if hasattr(cond, "resolve"):
                    cond.resolve(global_env, new_env)
                    if not cond.evaluate():
                        passed = False
                        break
                else:
                    # If it's a raw predicate function or falsy, treat accordingly
                    if not cond:
                        passed = False
                        break
            if not passed:
                continue

            # ── Recurse to handle subsequent clauses ───
            yield from _rec(idx + 1, new_env)

    # Kick off the recursion
    yield from _rec(0, {})
