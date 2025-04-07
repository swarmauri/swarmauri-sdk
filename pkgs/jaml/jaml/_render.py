import re
from .lark_nodes import DeferredExpression, PreservedString

def resolve_dotted(var, context):
    parts = var.split('.')
    curr = context
    for part in parts:
        if isinstance(curr, dict):
            curr = curr.get(part)
        else:
            return "${" + var + "}"  # fallback if not found
    return curr

def substitute_context_in_ast(ast_node, context):
    """
    Recursively traverse the AST (which may be a dict, list, or string) and replace 
    any occurrence of a deferred placeholder (${...}) with its value from the context.
    """
    if isinstance(ast_node, DeferredExpression):
        # For deferred expressions, evaluate them now using the merged environment.
        # Here, we assume that self-scope values for immediate expressions are
        # stored in the same part of the AST and can be used as the environment.
        # For simplicity, we use the provided context as the environment.
        return ast_node.evaluate(context)
    elif isinstance(ast_node, PreservedString):
        # Replace any ${...} in the unquoted value.
        s = ast_node.value
        substituted = re.sub(r'\$\{([^}]+)\}', lambda m: str(resolve_dotted(m.group(1).strip(), context)), s)
        return substituted
    elif isinstance(ast_node, str):
        substituted = re.sub(r'\$\{([^}]+)\}', lambda m: str(resolve_dotted(m.group(1).strip(), context)), ast_node)
        return substituted
    elif isinstance(ast_node, dict):
        return {k: substitute_context_in_ast(v, context) for k, v in ast_node.items()}
    elif isinstance(ast_node, list):
        return [substitute_context_in_ast(item, context) for item in ast_node]
    else:
        return ast_node