from typing import Dict, Any
import re
from .ast_nodes import (
    DeferredExpression, 
    PreservedString, 
    DeferredDictComprehension,
    DeferredListComprehension, 
    FoldedExpressionNode
)
from ._helpers import resolve_scoped_variable



from .ast_nodes import FoldedExpressionNode
from ._eval import safe_eval  # or import safe_eval as defined in resolve.py

def _render_folded_expression_node(node: FoldedExpressionNode, env: Dict[str, Any]) -> Any:
    """
    Process a FoldedExpressionNode at render time. This function does everything
    that resolve.py does (i.e. rebuilding and evaluating the inner expression) and then
    finally substitutes dynamic placeholders using the render-time environment.
    
    The difference from resolve.py is that here we finally resolve context-scoped variables.
    
    If a node has already been resolved to a non-string (e.g. an arithmetic result),
    return that value immediately.
    """
    print("[DEBUG RENDER] Rendering FoldedExpressionNode:", node)
    
    # If the node has a cached resolution that is not a string, return it immediately.
    if hasattr(node, 'resolved') and not isinstance(node.resolved, str):
        print("[DEBUG RENDER] Returning non-string cached resolution:", node.resolved)
        return node.resolved

    # Otherwise, if node.resolved is a string and it does not look like a folded expression, return it.
    # (This might be the case for f-string substitutions that are not numeric.)
    if hasattr(node, 'resolved') and isinstance(node.resolved, str):
        # Optionally, check if the node.original still starts with "<(".
        if not node.original.strip().startswith("<("):
            print("[DEBUG RENDER] Returning cached string resolution:", node.resolved)
            return node.resolved

    # Otherwise, process as before.
    folded_literal = node.original.strip()
    if not (folded_literal.startswith("<(") and folded_literal.endswith(")>")):
        return folded_literal

    def token_to_expr(token):
        print("[DEBUG RENDER] Processing token:", token)
        # Skip tokens representing the outer delimiters.
        if isinstance(token, str) and token.strip() in ("<(", ")>"):
            print("[DEBUG RENDER] Skipping delimiter token:", token)
            return ""
        if isinstance(token, (int, float)):
            return str(token)
        if hasattr(token, 'original'):
            return token.original
        if isinstance(token, str):
            if token.startswith('@{') or token.startswith('%{'):
                substituted_val = _substitute_vars(token, env)
                print("[DEBUG RENDER] Variable token substituted to:", substituted_val)
                return substituted_val
            elif token.startswith('${'):
                substituted_val = _substitute_vars(token, env)
                print("[DEBUG RENDER] Dynamic placeholder token substituted to:", substituted_val)
                return substituted_val
            else:
                return token
        if hasattr(token, 'children'):
            return " ".join(token_to_expr(child) for child in token.children)
        return str(token)

    expr_string = " ".join(token_to_expr(t) for t in node.content_tree.children).strip()
    print("[DEBUG RENDER] Rebuilt expression string:", expr_string)

    try:
        if re.fullmatch(r'[\d\s+\-*/().]+', expr_string):
            print("[DEBUG RENDER] Expression appears arithmetic. Using eval().")
            result = eval(compile(expr_string, "<string>", "eval"), {}, {})
        else:
            print("[DEBUG RENDER] Expression is non-arithmetic. Using safe_eval().")
            result = safe_eval(expr_string)
        print("[DEBUG RENDER] Evaluation result:", result)
    except Exception as e:
        print("[DEBUG RENDER] Exception during evaluation:", e)
        result = expr_string

    # Finally, perform dynamic placeholder substitution on the result (if it is a string).
    if isinstance(result, str):
        final_result = _substitute_vars(result, env)
    else:
        final_result = result

    print("[DEBUG RENDER] Final rendered result:", final_result)
    node.resolved = final_result  # Cache for later use.
    return final_result

def _substitute_vars(expr: str, env: Dict[str, Any], quote_strings: bool = True) -> str:
    """
    Replace occurrences of:
      - ${var} with the value from env (support dotted references)
      - @{var} (or dotted names) similarly,
      - and %{var} likewise.
    Uses _extract_value to ensure that if a variable is a PreservedString,
    its unquoted value is returned.
    
    If quote_strings is True, then any substituted string value will be returned in its
    Python-quoted representation (using repr).
    """
    def _extract_value(x: Any) -> Any:
        # Local import to avoid circular dependency.
        from .ast_nodes import PreservedString
        if isinstance(x, PreservedString):
            return x.value
        return x

    # Replace dynamic placeholders: ${...}
    def repl_dynamic(m):
        var = m.group(1).strip()
        keys = var.split('.')
        val = env
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return f"${{{var}}}"  # leave as-is if not found
        val = _extract_value(val)
        if quote_strings and isinstance(val, str):
            return repr(val)
        return str(val)

    result = re.sub(r'\$\{([^}]+)\}', repl_dynamic, expr)

    # Replace local references: %{var}
    def repl_local(m):
        var = m.group(1).strip()
        if var in env:
            val = _extract_value(env.get(var))
            if quote_strings and isinstance(val, str):
                return repr(val)
            return str(val)
        return f"%{{{var}}}"
    result = re.sub(r'%\{([^}]+)\}', repl_local, result)

    # Replace global references: @{var} or dotted names.
    def repl_global(m):
        var = m.group(1).strip()
        keys = var.split('.')
        val = env
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return f"@{{{var}}}"
        val = _extract_value(val)
        if quote_strings and isinstance(val, str):
            return repr(val)
        return str(val)
    result = re.sub(r'@\{([^}]+)\}', repl_global, result)

    return result



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

    if isinstance(ast_node, (DeferredExpression, DeferredDictComprehension, DeferredListComprehension)):
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



