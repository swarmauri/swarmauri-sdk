import re
from .lark_nodes import DeferredExpression, PreservedString, DeferredComprehension
from ._helpers import resolve_scoped_variable

def substitute_deferred(ast_node, env):
    """
    Traverse the AST recursively. For any DeferredExpression or DeferredComprehension node,
    call its evaluate() method with the provided environment and replace it with the evaluated result.
    Also, substitute any context placeholders (using ${...}) in plain strings.

    If 'env' is empty and 'ast_node' is a dict, then merge all top-level assignments
    (ignoring control keys like "__comments__") into the global environment.
    In the merge, if an assignment is stored as a dict with keys "_annotation" and "_value",
    then use its "_annotation" (which holds the original string) as the global value.
    """
    # Merge globals from the AST if env is empty.
    if isinstance(env, dict) and not env and isinstance(ast_node, dict):
        merged = {}
        for k, v in ast_node.items():
            if k == "__comments__":
                continue
            # Unwrap assignment wrappers.
            if isinstance(v, dict) and "_annotation" in v and "_value" in v:
                merged[k] = v["_annotation"]
            else:
                merged[k] = v
        env = merged

    if isinstance(ast_node, (DeferredExpression, DeferredComprehension)):
        return ast_node.evaluate(env)
    elif isinstance(ast_node, dict):
        return {k: substitute_deferred(v, env) for k, v in ast_node.items()}
    elif isinstance(ast_node, list):
        return [substitute_deferred(item, env) for item in ast_node]
    elif isinstance(ast_node, PreservedString):
        s = ast_node.original
        if s.lstrip().startswith("f\"") or s.lstrip().startswith("f'"):
            # Use evaluate_f_string to process the f-string with global scope markers
            from ._helpers import evaluate_f_string
            return evaluate_f_string(s.lstrip(), env, {})
        else:
            # Replace ${...} placeholders in the unquoted value.
            s = ast_node.value
            return re.sub(
                r'\$\{([^}]+)\}', 
                lambda m: str(resolve_scoped_variable(m.group(1).strip(), env) or m.group(0)), 
                s
            )
    elif isinstance(ast_node, str):
        if ast_node.lstrip().startswith("f\"") or ast_node.lstrip().startswith("f'"):
            from ._helpers import evaluate_f_string
            return evaluate_f_string(ast_node.lstrip(), env, {})
        else:
            return re.sub(
                r'\$\{([^}]+)\}', 
                lambda m: str(resolve_scoped_variable(m.group(1).strip(), env) or m.group(0)), 
                ast_node
            )
    else:
        return ast_node
