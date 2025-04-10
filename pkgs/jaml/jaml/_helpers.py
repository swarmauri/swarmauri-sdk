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

def evaluate_immediate_expression(expr, global_data, local_data):
    """
    Process an expression from a folded (immediate) evaluation.
    
    This function makes three passes:
      1. It replaces all occurrences of %{var} with the repr() of the corresponding value from local_data.
      2. It replaces all occurrences of @{var} (supporting dotted names) with the repr() of the corresponding value from global_data.
      3. It replaces all occurrences of ${...} with a quoted string so that these placeholders remain unresolved.
    
    Finally, it evaluates the resulting Python expression in a restricted environment.
    
    Examples:
      "b" + "c"           -> "bc"
      "value" + "${var}"   -> "value" + "${var}"  (left unresolved, so that later f-string interpolation can occur)
      2 + 3               -> 5
      true and X == X     -> evaluates with Python booleans (assuming X is defined in context)
    """
    # 1) Replace self-scope markers (%{...}) using local_data.
    def repl_local(match):
        var_name = match.group(1).strip()
        value = local_data.get(var_name)
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return repr(unquote(value.value))
        elif isinstance(value, str):
            return repr(unquote(value))
        return str(value)
    
    expr = re.sub(r'%{([^}]+)}', repl_local, expr)
    
    # 2) Replace global markers (@{...}) using global_data (supporting dotted names).
    def repl_global(match):
        var_name = match.group(1).strip()
        if '.' in var_name:
            value = resolve_scoped_variable(var_name, global_data)
        else:
            value = global_data.get(var_name)
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return repr(unquote(value.value))
        elif isinstance(value, str):
            return repr(unquote(value))
        return str(value)
    
    expr = re.sub(r'@{([^}]+)}', repl_global, expr)
    
    # 3) Replace context markers (${...}) by quoting them, so they remain in the final string.
    def repl_context(match):
        placeholder = match.group(0)  # e.g. "${auth_token}"
        return repr(placeholder)
    
    expr = re.sub(r'\$\{([^}]+)\}', repl_context, expr)
    
    # Now, evaluate the resulting expression in a safe environment.
    safe_globals = {"__builtins__": {}, "true": True, "false": False}
    try:
        result = eval(expr, safe_globals, {})
    except Exception as e:
        # In case evaluation fails, return the substituted expression.
        result = expr
    return result



def evaluate_f_string(f_str, global_data, local_data):
    """
    Evaluate an f-string by first evaluating its inner Python expression then
    substituting interpolations.

    Supports three kinds of markers:
      - Global markers: @{...} (looked up in global_data; supports dotted names)
      - Self/local markers: %{...} (looked up in local_data; supports dotted names)
      - Context markers: ${...} (looked up in global_data)
      
    f_str is assumed to start with f" or f'.
    """
    print("[DEBUG EVAL_F_STRING] Original f-string:", f_str)
    
    # Verify f-string starts with f" or f'
    if not (f_str.startswith('f"') or f_str.startswith("f'")):
        print("[DEBUG EVAL_F_STRING] Not an f-string; returning as-is.")
        return f_str

    # Remove the leading 'f' and surrounding quotes.
    inner = f_str[1:].lstrip()
    if inner and inner[0] in ('"', "'"):
        quote_char = inner[0]
        if inner.endswith(quote_char):
            inner = inner[1:-1]
        else:
            inner = inner[1:]
    print("[DEBUG EVAL_F_STRING] After removing f prefix and quotes, inner:", inner)
    
    # If the entire inner expression is wrapped in curly braces, remove them.
    inner_strip = inner.strip()
    if inner_strip.startswith("{") and inner_strip.endswith("}"):
        inner = inner_strip[1:-1].strip()
    print("[DEBUG EVAL_F_STRING] After removing surrounding curly braces, inner:", inner)
    
    # Attempt to evaluate the expression using safe_eval.
    try:
        evaluated = safe_eval(inner)
        print("[DEBUG EVAL_F_STRING] safe_eval result:", evaluated)
        result = str(evaluated)
    except Exception as e:
        print("[DEBUG EVAL_F_STRING] safe_eval failed with exception:", e)
        result = inner  # fallback to the raw inner expression if evaluation fails

    # Now perform the first pass of substitutions on the evaluated result.
    # This pass processes global (@) and local (%) markers.
    pattern = re.compile(r'([@%]){([^}]+)}')
    def repl(match):
        scope_marker = match.group(1)
        var_name = match.group(2).strip()
        if scope_marker == '@':
            # Global lookup: support dotted names.
            if '.' in var_name:
                value = resolve_scoped_variable(var_name, global_data)
            else:
                value = global_data.get(var_name, match.group(0))
        elif scope_marker == '%':
            # Self/local lookup.
            if '.' in var_name:
                value = resolve_scoped_variable(var_name, local_data)
            else:
                value = local_data.get(var_name, match.group(0))
        else:
            value = match.group(0)
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return unquote(value.value)
        elif isinstance(value, str):
            return unquote(value)
        return str(value)
    evaluated_sub = re.sub(pattern, repl, result)
    print("[DEBUG EVAL_F_STRING] After first pass substitution:", evaluated_sub)
    
    # Second pass: Process context markers ${...} using global_data.
    context_pattern = re.compile(r'\$\{([^}]+)\}')
    def context_repl(match):
        var_name = match.group(1).strip()
        value = resolve_scoped_variable(var_name, global_data)
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return unquote(value.value)
        elif isinstance(value, str):
            return unquote(value)
        return str(value)
    evaluated_sub = re.sub(context_pattern, context_repl, evaluated_sub)
    print("[DEBUG EVAL_F_STRING] Final evaluated f-string after context substitution:", evaluated_sub)
    
    return evaluated_sub


def evaluate_f_string_interpolation(f_str, env):
    """
    Evaluate a simple f-string (e.g. f"key_{x}") by substituting any
    occurrences of {var} with the corresponding value from env.
    Assumes f_str starts with f" or f'.
    """
    # Remove the leading f and the surrounding quotes.
    quote_char = f_str[1]
    inner = f_str[2:-1]  # for example: 'key_{x}'
    
    def repl(match):
        var_name = match.group(1).strip()
        return str(env.get(var_name, match.group(0)))
    
    return re.sub(r'\{([^}]+)\}', repl, inner)


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

