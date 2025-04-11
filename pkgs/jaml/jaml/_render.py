from typing import Dict, Any
import re
from .ast_nodes import (
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

    # If the node has a cached resolution that is a string and its origin
    # does not appear to be a folded expression, return it.
    if hasattr(node, 'resolved') and isinstance(node.resolved, str):
        if not node.origin.strip().startswith("<("):
            print("[DEBUG RENDER] Returning cached string resolution:", node.resolved)
            return node.resolved

    folded_literal = node.origin.strip()
    # If the origin is not wrapped with the folded markers, substitute its placeholders.
    if not (folded_literal.startswith("<(") and folded_literal.endswith(")>")):
        substituted_literal = _substitute_vars(folded_literal, env)
        print("[DEBUG RENDER] Folded literal without delimiters after substitution:", substituted_literal)
        return substituted_literal

    def token_to_expr(token):
        print("[DEBUG RENDER] Processing token:", token)
        # Skip tokens representing the outer delimiters.
        if isinstance(token, str) and token.strip() in ("<(", ")>"):
            print("[DEBUG RENDER] Skipping delimiter token:", token)
            return ""
        if isinstance(token, (int, float)):
            return str(token)
        if hasattr(token, 'origin'):
            return token.origin
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

    # Perform dynamic placeholder substitution on the result (if it is a string).
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
    print("[DEBUG SUB] Starting substitution in expression:", expr)
    print("[DEBUG SUB] Using env:", env)

    def _extract_value(x: Any) -> Any:
        from .ast_nodes import PreservedString
        if isinstance(x, PreservedString):
            print("[DEBUG SUB] Extracting value from PreservedString:", x.value)
            return x.value
        return x

    # Replace dynamic placeholders: ${...}
    def repl_dynamic(m):
        var = m.group(1).strip()
        print("[DEBUG SUB] Found dynamic placeholder for variable:", var)
        keys = var.split('.')
        val = env
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                print("[DEBUG SUB] Dynamic variable not found; leaving placeholder:", m.group(0))
                return f"${{{var}}}"
        val = _extract_value(val)
        substituted_val = repr(val) if quote_strings and isinstance(val, str) else str(val)
        print("[DEBUG SUB] Dynamic placeholder substituted to:", substituted_val)
        return substituted_val

    result = re.sub(r'\$\{([^}]+)\}', repl_dynamic, expr)
    print("[DEBUG SUB] After dynamic substitution:", result)

    # Replace local references: %{var}
    def repl_local(m):
        var = m.group(1).strip()
        print("[DEBUG SUB] Found local variable reference:", var)
        if var in env:
            val = _extract_value(env.get(var))
            substituted_val = repr(val) if quote_strings and isinstance(val, str) else str(val)
            print("[DEBUG SUB] Local reference substituted to:", substituted_val)
            return substituted_val
        print("[DEBUG SUB] Local variable not found; leaving placeholder:", m.group(0))
        return f"%{{{var}}}"
    result = re.sub(r'%\{([^}]+)\}', repl_local, result)
    print("[DEBUG SUB] After local substitution:", result)

    # Replace global references: @{var} or dotted names.
    def repl_global(m):
        var = m.group(1).strip()
        print("[DEBUG SUB] Found global variable reference:", var)
        keys = var.split('.')
        val = env
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                print("[DEBUG SUB] Global variable not found; leaving placeholder:", m.group(0))
                return f"@{{{var}}}"
        val = _extract_value(val)
        substituted_val = repr(val) if quote_strings and isinstance(val, str) else str(val)
        print("[DEBUG SUB] Global reference substituted to:", substituted_val)
        return substituted_val
    result = re.sub(r'@\{([^}]+)\}', repl_global, result)
    print("[DEBUG SUB] Final substitution result:", result)
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
    print("[DEBUG RENDER] Processing node of type:", type(ast_node), "with env:", env)

    # Unwrap annotated assignment nodes:
    if isinstance(ast_node, dict):
        keys = set(ast_node.keys())
        if keys == {"_annotation", "_value"}:
            print("[DEBUG RENDER] Unwrapping annotated node:", ast_node)
            return ast_node["_annotation"]

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
        print("[DEBUG RENDER] Merged environment for top-level dict:", env)

    if isinstance(ast_node, (DeferredDictComprehension, DeferredListComprehension)):
        print("[DEBUG RENDER] Evaluating deferred expression/comprehension for node:", ast_node)
        result = ast_node.evaluate(env)
        print("[DEBUG RENDER] Deferred expression evaluated to:", result)
        return result

    elif isinstance(ast_node, FoldedExpressionNode):
        print("[DEBUG RENDER] Processing FoldedExpressionNode:", ast_node)
        result = _render_folded_expression_node(ast_node, env)
        print("[DEBUG RENDER] FoldedExpressionNode rendered to:", result)
        return result
        
    elif isinstance(ast_node, dict):
        # Build a local environment for this section.
        local_env = {}
        if isinstance(env, dict):
            local_env.update(env)
        print("[DEBUG RENDER] Processing dict node with local_env:", local_env)
        for k, v in ast_node.items():
            if k == "__comments__":
                continue
            if isinstance(v, dict) and "_annotation" in v and "_value" in v:
                local_env[k] = v["_annotation"]
            else:
                local_env[k] = v
        result = { k: substitute_deferred(v, local_env) for k, v in ast_node.items() }
        print("[DEBUG RENDER] Finished processing dict node; result:", result)
        return result

    elif isinstance(ast_node, list):
        print("[DEBUG RENDER] Processing list node with env:", env)
        result = [substitute_deferred(item, env) for item in ast_node]
        print("[DEBUG RENDER] Finished processing list node; result:", result)
        return result

    elif isinstance(ast_node, PreservedString):
        s = ast_node.origin
        print("[DEBUG RENDER] Processing PreservedString:", s)
        if s.lstrip().startswith("f\"") or s.lstrip().startswith("f'"):
            print("[DEBUG RENDER] Detected f-string in PreservedString:", s)
            from ._helpers import evaluate_f_string
            result = evaluate_f_string(s.lstrip(), env, env)
            print("[DEBUG RENDER] evaluate_f_string result:", result)
            return result
        else:
            s = ast_node.value
            result = _substitute_vars(s, env)
            print("[DEBUG RENDER] Processed PreservedString without f-prefix; result:", result)
            return result

    elif isinstance(ast_node, str):
        print("[DEBUG RENDER] Processing string node:", ast_node)
        if ast_node.lstrip().startswith("f\"") or ast_node.lstrip().startswith("f'"):
            print("[DEBUG RENDER] Detected f-string in plain string:", ast_node)
            from ._helpers import evaluate_f_string
            result = evaluate_f_string(ast_node.lstrip(), env, env)
            print("[DEBUG RENDER] evaluate_f_string result for string node:", result)
            return result
        else:
            result = _substitute_vars(ast_node, env)
            print("[DEBUG RENDER] Processed plain string with substitution; result:", result)
            return result

    else:
        print("[DEBUG RENDER] Returning node as-is:", ast_node)
        return ast_node
