# jaml/_comprehension.py
from typing import Any, Dict, List, Optional, Iterator
from ._ast_nodes import BaseNode, ListComprehensionNode, DictComprehensionNode, ComprehensionClausesNode, AliasClauseNode
from ._eval import safe_eval

def evaluate_comprehension(node: BaseNode, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None) -> Any:
    local_env = local_env or {}
    context = context or {}
    result = []

    def iterate_clauses(clauses: List, env: Dict) -> Iterator[Dict]:
        if not clauses:
            yield env
            return
        clause = clauses[0]
        clause.iterable.resolve(global_env, env, context)
        iterable = clause.iterable.evaluate()
        if not isinstance(iterable, (list, tuple)):
            raise ValueError(f"Expected iterable in comprehension at line {clause.meta.line}, got {type(iterable)}")
        for item in iterable:
            temp_env = env.copy()
            for var in clause.loop_vars:
                if isinstance(var, AliasClauseNode):
                    var_name = var.scoped_var.value.lstrip('%{').rstrip('}')
                    temp_env[var_name] = item
                elif isinstance(var, BaseNode):
                    temp_env[var.value] = item
            if clause.conditions:
                conditions_pass = True
                for condition in clause.conditions:
                    condition.resolve(global_env, temp_env, context)
                    cond_value = condition.evaluate()
                    if cond_value is None:
                        conditions_pass = False  # null condition fails
                        break
                    if not cond_value:
                        conditions_pass = False
                        break
                if conditions_pass:
                    yield from iterate_clauses(clauses[1:], temp_env)
            else:
                yield from iterate_clauses(clauses[1:], temp_env)

    clauses = node.clauses.clauses if node.clauses else []
    for env in iterate_clauses(clauses, local_env):
        temp_env = local_env.copy()
        temp_env.update(env)
        if isinstance(node, ListComprehensionNode):
            node.header_expr.resolve(global_env, temp_env, context)
            value = node.header_expr.evaluate()
            result.append(value)  # Include null for MEP-0021
        elif isinstance(node, DictComprehensionNode):
            node.pair.resolve(global_env, temp_env, context)
            key, value = node.pair.evaluate()
            if key is not None:
                result.append((key, value))
    
    return result if isinstance(node, ListComprehensionNode) else dict(result)