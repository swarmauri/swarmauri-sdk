import re
from .lark_nodes import DeferredExpression, PreservedString, DeferredDictComprehension, FoldedExpressionNode
from ._helpers import resolve_scoped_variable, _render_folded_expression_node

def substitute_deferred(ast_node, env):
    """
    Recursively traverse the AST to replace deferred expressions and f-string placeholders.
    
    - For dictionary nodes, build a fresh local environment for that section by merging the parent
      environment with the section's own assignments. If an assignment is represented as a dict with 
      "_annotation" and "_value", then the _annotation (which is the original PreservedString) is used.
    - For f-string (PreservedString) nodes, evaluate the string using the current environment for both
      global (@ markers) and self-scope (% markers) lookups.
    """
    # If no environment is provided at the top level and ast_node is a dict,
    # merge top-level keys (skipping control keys) into the environment.
    if isinstance(env, dict) and not env and isinstance(ast_node, dict):
        merged = {}
        for k, v in ast_node.items():
            if k == "__comments__":
                continue
            # Unwrap assignment wrappers if present.
            if isinstance(v, dict) and "_annotation" in v and "_value" in v:
                merged[k] = v["_annotation"]
            else:
                merged[k] = v
        env = merged

    if isinstance(ast_node, (DeferredExpression, DeferredDictComprehension)):
        return ast_node.evaluate(env)

    elif isinstance(ast_node, FoldedExpressionNode):
        # Evaluate the folded expression using the environment,
        # returning a final string with both static and dynamic placeholders replaced.
        # If you only want partial sub for static references, you can do that, 
        # but MEP-0011 typically wants final dynamic placeholders replaced if context is given.

        return _render_folded_expression_node(ast_node, env)
        
    elif isinstance(ast_node, dict):
        # Build a local environment for this section.
        local_env = {}
        # Start with parent's environment.
        if isinstance(env, dict):
            local_env.update(env)
        # Then update with the current section's assignments.
        for k, v in ast_node.items():
            if k == "__comments__":
                continue
            if isinstance(v, dict) and "_annotation" in v and "_value" in v:
                local_env[k] = v["_annotation"]
            else:
                local_env[k] = v
        # Recurse into each key using the local environment.
        return { k: substitute_deferred(v, local_env) for k, v in ast_node.items() }

    elif isinstance(ast_node, list):
        return [substitute_deferred(item, env) for item in ast_node]

    elif isinstance(ast_node, PreservedString):
        s = ast_node.original
        if s.lstrip().startswith("f\"") or s.lstrip().startswith("f'"):
            # For f-strings, use evaluate_f_string with the current environment for both global and local lookups.
            from ._helpers import evaluate_f_string
            return evaluate_f_string(s.lstrip(), env, env)
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
            return evaluate_f_string(ast_node.lstrip(), env, env)
        else:
            return re.sub(
                r'\$\{([^}]+)\}',
                lambda m: str(resolve_scoped_variable(m.group(1).strip(), env) or m.group(0)),
                ast_node
            )
    else:
        return ast_node
