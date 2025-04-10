"""
_resolve.py

Implements 'resolve_ast' for MEP-0011b, transforming an AST by evaluating
all static expressions based on built-in global/local scope references.
Context references (${...}) remain intact for the render phase.

Usage:
    from ._resolve import resolve_ast

    optimized_ast = resolve_ast(original_ast)
"""
from typing import Dict, Any
from copy import deepcopy
from .lark_nodes import PreservedString

# If you have custom node classes, import them here:
# from .lark_nodes import FoldedExpression, PreservedString, ...
# from ._helpers import evaluate_immediate_expression, ...

#######################################
# 1) Entry Point
#######################################

def resolve_ast(ast):
    """
    Recursively walk the AST, replacing static expressions with their computed values,
    while leaving dynamic references untouched.

    :param ast: The AST produced by the load/parse phase (e.g. round_trip_loads()).
    :return: A new AST (or possibly updated in-place) with static expressions resolved.
    """
    # We make a deep copy to avoid mutating the original AST if you prefer immutability:
    ast_copy = deepcopy(ast)

    # First, gather a top-level 'global' environment from the AST if relevant.
    global_env = _build_global_env(ast_copy)

    # Recursively traverse and resolve:
    resolved = _resolve_node(ast_copy, global_env, local_scopes={})
    return resolved


#######################################
# 2) Build Global Environment
#######################################

def _build_global_env(ast):
    global_env = {}
    for k, v in ast.items():
        # Skip internal keys like __comments__, or sub-sections
        if k.startswith("__"):
            continue
        if _is_static_value(v):
            if isinstance(v, PreservedString):
                global_env[k] = v.value
            else:
                global_env[k] = v
    return global_env



#######################################
# 3) Recursive Resolution
#######################################

def _resolve_node(node, env, local_scopes):
    """
    Recursively resolve a node in the AST using the given environment (env).
    local_scopes: a stack or dictionary used for handling nested sections.

    :param node:  The current part of the AST (dict, list, expression object, etc).
    :param env:   The environment with global + local definitions so far.
    :param local_scopes: helps track local scope if you nest sections.
    :return: A resolved version of the node.
    """

    # 1) If node is a dictionary, handle sections/assignments.
    if isinstance(node, dict):
        return _resolve_dict(node, env, local_scopes)

    # 2) If node is a list, resolve each element.
    elif isinstance(node, list):
        return [_resolve_node(item, env, local_scopes) for item in node]

    # 3) If node is an expression object (Folded, etc).
    elif _is_folded_expression(node):
        return _resolve_folded_expression(node, env)

    # 4) If node is an unquoted literal or some other structure:
    #    We can check if it references a static or dynamic variable,
    #    or is purely a string/integer/etc.
    elif _requires_partial_eval(node):
        return _partial_eval(node, env)

    elif isinstance(node, PreservedString):
        # If it starts with f" or f', attempt to resolve references:
        if node.original.lstrip().startswith("f\"") or node.original.lstrip().startswith("f'"):
            # This is an f-string
            resolved_str = _maybe_resolve_fstring(node.original, env)
            # If it has no dynamic placeholders left, that’s our final string
            return resolved_str

    else:
        # The node is presumably a literal or already computed value
        return node


def _resolve_dict(dct, env, local_scopes):
    """
    Resolve a dictionary that might represent a section or an assignment map.

    If your AST structure uses special keys for sections, you'd detect that here.
    Then you can build local environments for each section, etc.
    """
    # Potentially check if this dict is a "section"
    # e.g. if dct.get("__section_name__") or something like that
    local_env = env.copy()  # shallow copy

    # If you store local assignments in the same dictionary, gather them to local_env
    # for k, v in dct.items():
    #     if is_local_assignment(k, v):
    #         # Evaluate if it's purely static or store as local_env
    #         pass

    resolved_dict = {}
    for k, v in dct.items():
        # If the item is a section name or a special comment key, handle accordingly
        if k.startswith("__"):
            resolved_dict[k] = v
            continue

        # Otherwise, recursively resolve
        resolved_val = _resolve_node(v, local_env, local_scopes)
        resolved_dict[k] = resolved_val

        # If we consider this an assignment that belongs to local_env, we might do:
        # if _is_static_value(resolved_val):
        #     local_env[k] = resolved_val

    return resolved_dict

#######################################
# 4) Evaluating Expressions
#######################################

def _is_folded_expression(node):
    """
    Detect if the node is a 'FoldedExpression' object or similar.
    You might check:
      isinstance(node, FoldedExpression)
      or node.__class__.__name__ == "FoldedExpression"
    """
    # Example:
    # return hasattr(node, 'is_folded_expr') and node.is_folded_expr
    return False


def _resolve_folded_expression(expr, env):
    """
    If expr is a purely static expression referencing only env variables, evaluate it.
    If it references context placeholders, partially evaluate the static parts and keep placeholders.
    """
    # 1) Extract the expression string, e.g. expr.inner_text
    expression_str = expr.expr  # or however you store it

    # 2) Check if it references ${...} or not
    if _references_context(expression_str):
        # partial evaluation logic
        return _partial_fold(expr, env)
    else:
        # full static evaluation
        try:
            # e.g. parse the expression into Python, or use custom evaluate_immediate_expression
            substituted = _substitute_static_vars(expression_str, env)
            result = eval(substituted, {"__builtins__": {}}, {"true": True, "false": False})
            return result
        except Exception:
            # fallback, or keep as is
            return expr

def _references_context(expression_str):
    """
    Return True if the expression has a ${...} reference or
    anything that is dynamic.
    """
    import re
    return bool(re.search(r"\$\{\s*[^}]+\}", expression_str))

def _partial_fold(expr, env):
    """
    If an expression is partly static and partly dynamic, evaluate
    what we can, fold the rest into an f-string or similar mechanism.
    """
    # Possibly do partial string parsing. If your code is simpler, you might
    # do minimal partial resolution and return a new expression object.
    return expr  # placeholder, or produce new partially resolved object

def _substitute_static_vars(expression_str, env):
    """
    Replace occurrences of @{var} or %{var} in expression_str using env.
    """
    # This is project-specific. A naive approach with regex:
    import re

    def repl(m):
        var_name = m.group(1)
        return str(env.get(var_name, f"@{{{var_name}}}"))  # fallback to original text if not found

    # Example for matching @ or % with a pattern like: @{something}
    # Adjust for your actual grammar
    expression_str = re.sub(r'[@%]\{([^}]+)\}', repl, expression_str)
    return expression_str

#######################################
# 5) Partial Eval + Helpers
#######################################

def _requires_partial_eval(node):
    """
    Return True if 'node' is some kind of intermediate expression
    that might need partial evaluation (like a string referencing @ or %).
    """
    # This depends on your structure. If node is a string containing
    # references, or an object with markers, you'd detect it here.
    return False

def _partial_eval(node, env):
    """
    Evaluate the static portion, keep dynamic references intact.
    Possibly fold into an f-string.
    """
    # Implementation details vary heavily on your grammar
    return node

def _is_static_value(x):
    """
    Return True if x is a literal or a PreservedString with no context placeholders.
    """
    if isinstance(x, PreservedString):
        # if we detect ${ in the string, it's not purely static
        if "${" in x.value:
            return False
        return True
    if isinstance(x, str):
        if "${" in x:
            return False
        return True
    return isinstance(x, (int, float, bool, type(None)))



def _maybe_resolve_fstring(fstring_value: str, env: Dict[str, Any]) -> str:
    """
    If `fstring_value` references only static global/local variables (@{ or %{ }),
    fully substitute them using `env`. Return the final plain string if successful.
    If there's a dynamic placeholder (${...}), keep it partially resolved or skip.
    """
    # 1) Check if there's any dynamic placeholder ${...}:
    import re
    has_context = re.search(r"\$\{\s*[^}]+\}", fstring_value)
    if has_context:
        # We'll skip full resolution here, might do partial
        return fstring_value  # or partially evaluate

    # 2) If no ${...}, let's do a direct substitution for @% variables:
    # For example, f"@{base}/config.toml" -> "/home/user/config.toml"
    # then we can remove the leading f" and trailing "
    # but you likely store it as e.g. fstring_value = 'f"@{base}/config.toml"'
    # so parse out the actual content inside quotes:
    inner_str = fstring_value.lstrip()[1:]  # remove leading f
    if inner_str.startswith('"') or inner_str.startswith("'"):
        inner_str = inner_str[1:-1]  # remove surrounding quotes

    # Replace @% references:
    def repl(m):
        var_name = m.group(1)
        return str(env.get(var_name, f"@{{{var_name}}}"))

    # Regex to match @{something} or %{something}
    replaced = re.sub(r'[@%]\{([^}]+)\}', repl, inner_str)

    # Now replaced is e.g. "/home/user/config.toml"
    return replaced
