# jaml/_comprehension.py
from __future__ import annotations
from typing import Dict, Iterator, Optional, Union, List, Any
from ._eval import safe_eval
import re
print('[_comprehension] module loaded')


# ④ evaluate list- and dict-comprehension strings
list_comp_pattern = re.compile(r'^\s*\[.*\bfor\b.*\]\s*$')
dict_comp_pattern = re.compile(r'^\s*\{.*\bfor\b.*\}\s*$')

def _eval_comprehensions(obj: Any) -> Any:
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
            python_syntax = re.sub(r'=(?=[^}]*\bfor\b)', ':', obj)
            try:
                return eval(python_syntax)
            except Exception:
                return obj
    return obj

def _evaluate_comprehension(node, global_env, context=None):
    from ._ast_nodes import ListComprehensionNode
    print(f'[_evaluate_comprehension] entering: node={node}, global_env_keys={list(global_env.keys())}, context={context}')
    results = []
    for env in iter_environments(node.clauses, global_env, {}, context or {}):
        print(f'[_evaluate_comprehension] iteration env={env}')
        # resolve header_expr (for lists) or pair (for dicts)
        if hasattr(node, 'header_expr'):
            print(f'[_evaluate_comprehension] resolving header_expr: {node.header_expr}')
            node.header_expr.resolve(global_env, env)
            print(f'[_evaluate_comprehension] resolved header_expr.resolved={node.header_expr.resolved}')
            results.append(node.header_expr.resolved)
        else:
            print(f'[_evaluate_comprehension] resolving pair: {node.pair}')
            node.pair.resolve(global_env, env)
            k, v = node.pair.resolved
            print(f'[_evaluate_comprehension] resolved pair -> key={k}, value={v}')
            results.append((k, v))
    # for dict comprehensions, you’d turn results into a dict
    if isinstance(node, ListComprehensionNode):
        print(f'[_evaluate_comprehension] returning list of length {len(results)}')
        return results
    else:
        result_dict = dict(results)
        print(f'[_evaluate_comprehension] returning dict of size {len(result_dict)}')
        return result_dict


def iter_environments(clauses, global_env, local_env, context):
    print(f'[iter_environments] entering: clauses={clauses}, global_env_keys={list(global_env.keys())}, local_env={local_env}, context={context}')
    clause_list = clauses.clauses

    def _rec(idx, env):
        print(f'[iter_environments._rec] idx={idx}, current_env={env}')
        if idx == len(clause_list):
            print(f'[iter_environments._rec] idx == len, yielding env {env}')
            yield env
            return

        clause = clause_list[idx]
        # Determine iterable values, resolving if necessary
        iterable = clause.iterable
        if hasattr(iterable, "resolve"):
            print(f'[iter_environments._rec] resolving iterable: {iterable}')
            iterable.resolve(global_env, {**local_env, **env})
            iterable_vals = getattr(iterable, "resolved", []) or []
            print(f'[iter_environments._rec] resolved iterable_vals={iterable_vals}')
        else:
            iterable_vals = iterable or []
            print(f'[iter_environments._rec] using raw iterable_vals={iterable_vals}')

        for item in iterable_vals:
            new_env = {**env}

            # ── Bind loop variables ───────────────
            if hasattr(clause, "loop_vars") and clause.loop_vars:
                for var in clause.loop_vars:
                    name = getattr(var, "value", var)
                    new_env[name] = item
                print(f'[iter_environments._rec] bound loop_vars, new_env={new_env}')
            elif hasattr(clause, "loop_var"):
                new_env[clause.loop_var.value] = item
                print(f'[iter_environments._rec] bound loop_var, new_env={new_env}')
            else:
                print(f'[iter_environments._rec] no loop_var(s) to bind, skipping item {item}')
                continue

            # ── Apply any 'if' conditions ─────────
            passed = True
            for cond in getattr(clause, "conditions", []):
                print(f'[iter_environments._rec] evaluating condition: {cond}')
                if hasattr(cond, "resolve"):
                    cond.resolve(global_env, new_env)
                    cond_result = cond.evaluate()
                    print(f'[iter_environments._rec] condition resolved result={cond_result}')
                    if not cond_result:
                        passed = False
                        break
                else:
                    if not cond:
                        passed = False
                        print(f'[iter_environments._rec] raw condition falsy, skipping')
                        break
            if not passed:
                print(f'[iter_environments._rec] conditions not passed, continue to next item')
                continue

            # ── Recurse to handle subsequent clauses ───
            yield from _rec(idx + 1, new_env)

    # Kick off the recursion
    yield from _rec(0, {})
