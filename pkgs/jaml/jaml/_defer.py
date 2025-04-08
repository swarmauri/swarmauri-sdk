"""
Render helpers
"""
import re
from .lark_nodes import DeferredExpression, PreservedString, DeferredComprehension
from ._helpers import resolve_scoped_variable

def substitute_deferred(ast_node, env):
    """
    Traverse the AST recursively. For any DeferredExpression or DeferredComprehension node,
    call its evaluate() method with the provided environment and replace it with the evaluated result.
    Also, substitute any context placeholders (using ${...}) in plain strings.
    """
    if isinstance(ast_node, (DeferredExpression, DeferredComprehension)):
        return ast_node.evaluate(env)
    elif isinstance(ast_node, dict):
        return {k: substitute_deferred(v, env) for k, v in ast_node.items()}
    elif isinstance(ast_node, list):
        return [substitute_deferred(item, env) for item in ast_node]
    elif isinstance(ast_node, PreservedString):
        # Replace ${...} placeholders in the unquoted value.
        s = ast_node.value
        return re.sub(
            r'\$\{([^}]+)\}', 
            lambda m: str(resolve_scoped_variable(m.group(1).strip(), env) or m.group(0)), 
            s
        )
    elif isinstance(ast_node, str):
        return re.sub(
            r'\$\{([^}]+)\}', 
            lambda m: str(resolve_scoped_variable(m.group(1).strip(), env) or m.group(0)), 
            ast_node
        )
    else:
        return ast_node
