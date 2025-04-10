"""
_resolve.py

Handles global/local references, folded expressions, and partial evaluation. 
"""

from typing import Dict, Any
from copy import deepcopy
import re
import ast
import operator as op
from .ast_nodes import PreservedString, DeferredDictComprehension, FoldedExpressionNode, DeferredListComprehension

#######################################
# 1) Public Entry Point
#######################################

def resolve_ast(ast: dict) -> dict:
    ast_copy = deepcopy(ast)
    global_env = _build_global_env(ast_copy)
    return _resolve_node(ast_copy, global_env, local_env=None)


def _build_global_env(ast: dict) -> Dict[str, Any]:
    global_env = {}
    # top-level static assignments
    for k, v in ast.items():
        if k.startswith("__"):
            continue
        if not isinstance(v, dict) and _is_static_value(v):
            global_env[k] = _extract_value(v)
    # also gather per-section
    for k, v in ast.items():
        if k.startswith("__"):
            continue
        if isinstance(v, dict):
            section_env = {}
            for subk, subv in v.items():
                if not subk.startswith("__") and _is_static_value(subv):
                    section_env[subk] = _extract_value(subv)
            if section_env:
                global_env[k] = section_env
    return global_env


def _resolve_node(node: Any, global_env: Dict[str, Any], local_env: Dict[str, Any]) -> Any:
    if isinstance(node, dict):
        return _resolve_dict(node, global_env, local_env)

    elif isinstance(node, list):
        return [_resolve_node(item, global_env, local_env) for item in node]

    elif isinstance(node, DeferredDictComprehension):
        # Evaluate deferred comprehensions using the merged environment.
        env = {}
        env.update(global_env)
        if local_env:
            env.update(local_env)
        return node.evaluate(env)

    elif isinstance(node, DeferredListComprehension):
        env = {}
        env.update(global_env)
        if local_env:
            env.update(local_env)
        return node.evaluate(env)


    elif isinstance(node, PreservedString):
        # check f-string prefix
        stripped = node.original.lstrip()
        if stripped.startswith("f\"") or stripped.startswith("f'"):
            return _maybe_resolve_fstring(node.original, global_env, local_env)
        else:
            return node.value

    elif isinstance(node, str):
        # if a plain string starts with f", treat it as an f-string
        sstr = node.lstrip()
        if sstr.startswith("f\"") or sstr.startswith("f'"):
            return _maybe_resolve_fstring(node, global_env, local_env)
        else:
            return node

    elif isinstance(node, FoldedExpressionNode):
        # new branch for folded expressions
        return _resolve_folded_expression_node(node, global_env, local_env)
    else:
        return node


def _resolve_dict(dct: dict, global_env: Dict[str, Any], parent_local_env: Dict[str, Any]) -> dict:
    section_local_env = dict(parent_local_env or {})
    # if named section
    if "__section__" in dct:
        for k, v in dct.items():
            if not k.startswith("__") and _is_static_value(v):
                section_local_env[k] = _extract_value(v)
    resolved = {}
    for k, v in dct.items():
        if k.startswith("__"):
            resolved[k] = v
            continue
        rv = _resolve_node(v, global_env, section_local_env)
        resolved[k] = rv
        if _is_static_value(rv):
            section_local_env[k] = _extract_value(rv)
    return resolved

########################################
# 4) Expression Handling
########################################

def _maybe_resolve_fstring(fstring_literal: str, global_env: dict, local_env: dict) -> str:
    # If there are dynamic ${...} placeholders, simply return the original.
    if re.search(r"\$\{\s*[^}]+\}", fstring_literal):
        return fstring_literal
    
    # Remove the "f" prefix and surrounding quotes.
    inner = fstring_literal.lstrip()[1:]
    if inner.startswith('"') or inner.startswith("'"):
        inner = inner[1:-1]
    
    # For f-string resolution, do not add extra quotes.
    return _substitute_vars(inner, global_env, local_env, quote_strings=False)



def safe_eval(expr: str) -> any:
    """
    Safely evaluate a simple arithmetic or string concatenation expression.
    Only allows a fixed set of binary and unary operations and literals.
    """
    allowed_operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod,
        ast.Pow: op.pow,
        "true": True,
        "false": False
    }
    
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Name):  # Python 3.8+
            return f"{node.name}"
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type not in allowed_operators:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            return allowed_operators[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            else:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        else:
            raise ValueError(f"Unsupported expression element: {node}")
    
    tree = ast.parse(expr, mode='eval')
    return _eval(tree)

def _resolve_folded_expression_node(node, global_env, local_env) -> any:
    """
    For a FoldedExpressionNode, perform variable substitution and try to
    evaluate the entire expression using its parsed content_tree.

    The process is as follows:
      - Walk the content_tree and rebuild the expression string, applying:
          * Variable substitution (for tokens like @{...} or %{...})
          * Wrapping dynamic placeholders (${...}) in quotes.
          * Skipping tokens that represent the outer delimiters ("<(" and ")>")
      - If the rebuilt expression appears to be purely arithmetic,
        evaluate it directly with eval().
      - Otherwise, try to evaluate the expression with safe_eval().
      - If the result is a string that still contains a dynamic placeholder,
        assume it must be an f-string and prefix it appropriately.
      - Cache the evaluated result in node.resolved.
    """
    # Return a cached resolution if it exists.
    if hasattr(node, 'resolved'):
        print("[DEBUG] Returning cached resolution:", node.resolved)
        return node.resolved

    # Fallback if the content_tree is missing.
    if not hasattr(node, 'content_tree') or node.content_tree is None:
        print("[DEBUG] No content_tree found, using original")
        folded_literal = node.original
        stripped = folded_literal.strip()
        if not (stripped.startswith("<(") and stripped.endswith(")>")):
            node.resolved = folded_literal
            return folded_literal

        inner = stripped[2:-2].strip()
        substituted = _substitute_vars(inner, global_env, local_env, quote_strings=True)
        substituted_fixed = re.sub(r'(\$\{\s*[^}]+\})', r'"\1"', substituted)
        try:
            result = safe_eval(substituted_fixed)
            print("[DEBUG] Fallback safe_eval result:", result)
            if isinstance(result, str) and '${' in result:
                result = 'f"' + result + '"'
            node.resolved = result
            # Do not update node.original when result is not a string.
            return result
        except Exception as e:
            print("[DEBUG] Exception during fallback safe_eval:", e)
            node.resolved = substituted_fixed
            return substituted_fixed

    # Helper: Convert each token from the content tree into its expression form.
    def token_to_expr(token):
        print("[DEBUG] Processing token:", token)
        # Skip tokens representing the outer delimiters.
        if isinstance(token, str) and token.strip() in ("<(", ")>"):
            print("[DEBUG] Skipping delimiter token:", token)
            return ""
        # If token is a numeric literal, return its string representation.
        if isinstance(token, (int, float)):
            return str(token)
        # If the token object has an 'original' attribute, use that.
        if hasattr(token, 'original'):
            return token.original
        # If the token is a string:
        if isinstance(token, str):
            if token.startswith('@{') or token.startswith('%{'):
                substituted_val = _substitute_vars(token, global_env, local_env, quote_strings=True)
                print("[DEBUG] Variable token substituted to:", substituted_val)
                return substituted_val
            elif token.startswith('${'):
                wrapped = '"' + token + '"'
                print("[DEBUG] Dynamic placeholder token wrapped to:", wrapped)
                return wrapped
            else:
                return token
        # If token is a subtree (nested expression), recursively process its children.
        if hasattr(token, 'children'):
            return " ".join(token_to_expr(child) for child in token.children)
        # Fallback: simply convert token to string.
        return str(token)

    # Rebuild the inner expression from the content tree.
    expr_string = " ".join(token_to_expr(t) for t in node.content_tree.children).strip()
    print("[DEBUG] Rebuilt expression string:", expr_string)
    
    try:
        # If the expression looks purely arithmetic (only digits, operators,
        # whitespace, parentheses, or a period), then directly evaluate using eval().
        if re.fullmatch(r'[\d\s+\-*/().]+', expr_string):
            print("[DEBUG] Expression appears arithmetic. Using eval().")
            result = eval(compile(expr_string, "<string>", "eval"), {}, {})
        else:
            print("[DEBUG] Expression is non-arithmetic. Using safe_eval().")
            result = safe_eval(expr_string)
        
        print("[DEBUG] Evaluation result:", result)
        
        # If the evaluated result is a string with dynamic placeholders, convert to f-string.
        if isinstance(result, str) and '${' in result:
            result = 'f"' + result + '"'
            print("[DEBUG] Adjusted result to f-string:", result)
            
        node.resolved = result
        # For arithmetic (non-string) results, do NOT update node.original.
        # This preserves the original folded expression for potential round-trip needs.
        return result
    except Exception as e:
        print("[DEBUG] Exception during evaluation:", e)
        node.resolved = expr_string
        return expr_string


def _substitute_vars(expr: str, global_env: dict, local_env: dict, quote_strings: bool = True) -> str:
    """
    Replace local (%{var}) and global (@{var}) references.
    
    If quote_strings is True, any substituted string value will be returned in its
    Python-quoted representation (via repr) so that when evaluating the expression,
    it will be treated as a literal. If False (as for f-string processing), the raw value is used.
    """
    def repl_local(m):
        var = m.group(1).strip()
        if local_env and var in local_env:
            value = local_env[var]
            if quote_strings and isinstance(value, str):
                return repr(value)
            return str(value)
        return f"%{{{var}}}"
    
    tmp = re.sub(r'%\{([^}]+)\}', repl_local, expr)

    def repl_global(m):
        var = m.group(1).strip()
        if '.' in var:
            section, key = var.split('.', 1)
            sect_val = global_env.get(section)
            if isinstance(sect_val, dict) and key in sect_val:
                value = sect_val[key]
                if quote_strings and isinstance(value, str):
                    return repr(value)
                return str(value)
        if var in global_env:
            value = global_env[var]
            if quote_strings and isinstance(value, str):
                return repr(value)
            return str(value)
        return f"@{{{var}}}"
    
    replaced = re.sub(r'@\{([^}]+)\}', repl_global, tmp)
    return replaced




def _has_dynamic_placeholder(s: str) -> bool:
    return bool(re.search(r"\$\{\s*[^}]+\}", s))

########################################
# 5) Utility
########################################

def _is_static_value(x: Any) -> bool:
    if isinstance(x, PreservedString):
        return "${" not in x.value
    if isinstance(x, str):
        return "${" not in x
    return isinstance(x, (int, float, bool, type(None)))

def _extract_value(x: Any) -> Any:
    if isinstance(x, PreservedString):
        return x.value
    return x
