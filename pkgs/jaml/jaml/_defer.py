"""
Render helpers
"""
import re
from .lark_nodes import DeferredExpression, PreservedString

def substitute_deferred(ast_node, env):
    """
    Recursively traverse the AST. If you encounter a DeferredExpression,
    call its evaluate() method with the environment and replace it with the result.
    """
    if isinstance(ast_node, DeferredExpression):
        # Evaluate the deferred expression with the given environment.
        return ast_node.evaluate(env)
    elif isinstance(ast_node, dict):
        return {k: substitute_deferred(v, env) for k, v in ast_node.items()}
    elif isinstance(ast_node, list):
        return [substitute_deferred(item, env) for item in ast_node]
    elif isinstance(ast_node, PreservedString):
        # Optionally, also substitute any ${...} placeholders in preserved strings.
        s = ast_node.value  # use the inner unquoted value
        return re.sub(r'\$\{([^}]+)\}', lambda m: str(env.get(m.group(1).strip(), m.group(0))), s)
    elif isinstance(ast_node, str):
        return re.sub(r'\$\{([^}]+)\}', lambda m: str(env.get(m.group(1).strip(), m.group(0))), ast_node)
    else:
        return ast_node

