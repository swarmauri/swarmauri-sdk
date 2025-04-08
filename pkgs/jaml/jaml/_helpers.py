import re

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
    Substitute all occurrences of %{var} in expr using values from local_data.
    Return a valid Python expression as a string.
    """
    pattern = re.compile(r'%{([^}]+)}')
    def repl(match):
        var_name = match.group(1).strip()
        value = local_data.get(var_name, match.group(0))
        if value is None:
            return match.group(0)
        # Use repr() so the substituted value becomes a proper Python literal.
        if hasattr(value, 'value'):
            return repr(unquote(value.value))
        elif isinstance(value, str):
            return repr(unquote(value))
        return str(value)
    return re.sub(pattern, repl, expr)


def evaluate_f_string(f_str, global_data, local_data):
    """
    Evaluate an f-string by substituting interpolations.
    This function supports two kinds of markers:
      - Global markers: @{...} (using global_data, with dotted names resolved in global_data)
      - Self/local markers: %{...} (using local_data, with dotted names resolved in local_data)
      
    f_str is assumed to start with f" or f'
    """
    # Remove the leading f and surrounding quotes.
    inner = f_str[2:-1]

    # This regex now captures a scope marker (@ or %) and the variable name.
    pattern = re.compile(r'([@%]){([^}]+)}')
    
    def repl(match):
        scope_marker = match.group(1)
        var_name = match.group(2).strip()
        if scope_marker == '@' or '%':
            # For unscoped globals, if there is no dot, look in __default__.
            if '.' in var_name:
                value = resolve_scoped_variable(var_name, global_data)
            else:
                value = global_data.get(var_name, match.group(0))
        else:
            value = match.group(0)
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return unquote(value.value)
        elif isinstance(value, str):
            return unquote(value)
        return str(value)

    evaluated = re.sub(pattern, repl, inner)
    return evaluated

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