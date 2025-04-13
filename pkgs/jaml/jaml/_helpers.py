import re
from typing import Dict, Any

from ._eval import safe_eval

def unquote(s):
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def resolve_scoped_variable(var_name, data):
    """Resolve a dotted variable name in the configuration AST.
    
    For example, if var_name is 'path.base', then traverse data to return:
      data["path"]["base"]
    """
    parts = var_name.split('.')
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current

def evaluate_f_string(f_str, global_data, local_data, context=None):
    """
    Evaluate an f-string with:
      - Global markers: @{...} (global_data)
      - Local markers: %{...} (local_data)
      - Context markers: ${...} (context)
      - Unmarked variables: {var} (local_data, e.g., loop variables)
      - Unmarked expressions: {expr} (evaluated via safe_eval)
    """
    print("[DEBUG EVAL_F_STRING] Original f-string:", f_str)
    
    if not (f_str.startswith('f"') or f_str.startswith("f'")):
        print("[DEBUG EVAL_F_STRING] Not an f-string; returning as-is.")
        return f_str

    # Remove f prefix and quotes
    inner = f_str[1:].lstrip()
    if inner and inner[0] in ('"', "'"):
        quote_char = inner[0]
        if inner.endswith(quote_char):
            inner = inner[1:-1]
        else:
            inner = inner[1:]
    print("[DEBUG EVAL_F_STRING] After removing f prefix and quotes, inner:", inner)
    
    # Substitute placeholders and expressions
    pattern = re.compile(r'([@%\$])?\{([^}]+)\}')
    def repl(match):
        scope_marker = match.group(1)
        content = match.group(2).strip()
        print("[DEBUG EVAL_F_STRING] Processing content:", content, "marker:", scope_marker)

        value = None
        if scope_marker == '@':
            # Global lookup
            keys = content.split('.')
            val = global_data if global_data is not None else {}
            for key in keys:
                if isinstance(val, dict) and key in val:
                    val = val[key]
                else:
                    val = None
                    break
            value = val
        elif scope_marker == '%':
            # Local lookup
            keys = content.split('.')
            val = local_data if local_data is not None else {}
            for key in keys:
                if isinstance(val, dict) and key in val:
                    val = val[key]
                else:
                    val = None
                    break
            value = val
        elif scope_marker == '$':
            # Context lookup
            keys = content.split('.')
            val = context if context is not None else {}
            for key in keys:
                if isinstance(val, dict) and key in val:
                    val = val[key]
                else:
                    val = None
                    break
            value = val
        else:
            # Unmarked: try as variable, then as expression
            keys = content.split('.')
            val = local_data if local_data is not None else {}
            for key in keys:
                if isinstance(val, dict) and key in val:
                    val = val[key]
                else:
                    val = None
                    break
            value = val
            if value is None:
                # Try evaluating as an expression
                try:
                    value = safe_eval(content, local_env=local_data)
                    print("[DEBUG EVAL_F_STRING] Evaluated expression:", content, "to:", value)
                except Exception as e:
                    print("[DEBUG EVAL_F_STRING] Expression evaluation failed:", e)
                    return match.group(0)

        if value is None:
            print("[DEBUG EVAL_F_STRING] Content unresolved:", match.group(0))
            return match.group(0)
        if hasattr(value, 'value'):
            return unquote(value.value)
        elif isinstance(value, str):
            return unquote(value)
        return str(value)

    result = re.sub(pattern, repl, inner)
    print("[DEBUG EVAL_F_STRING] After substitution:", result)
    
    # Only apply safe_eval if result is a valid expression
    if re.match(r'^[\d\s+\-*/().]+$|^(true|false|null)$', result):
        try:
            evaluated = safe_eval(result, local_env=local_data)
            print("[DEBUG EVAL_F_STRING] safe_eval result:", evaluated)
            return str(evaluated)
        except Exception as e:
            print("[DEBUG EVAL_F_STRING] safe_eval failed:", e)
    return result



def evaluate_comprehension(expr_node, env):
    """
    Evaluate an arithmetic expression from a comprehension.
    If expr_node is a Tree (for example, an arithmetic expression), 
    join its children into a string (with spaces) and evaluate it.
    If it is not a Tree, assume it is already a literal value.
    """
    from lark import Tree, Token
    if isinstance(expr_node, Tree):
        # Join the string representations of the children.
        expr_str = " ".join(str(child) for child in expr_node.children)
        try:
            # Evaluate using the provided environment.
            return eval(expr_str, {"__builtins__": {}}, env)
        except Exception as e:
            # Fallback: return the raw expression string if evaluation fails.
            return expr_str
    elif isinstance(expr_node, Token):
        return expr_node.value
    else:
        # Otherwise, assume it's already a computed value.
        return expr_node

