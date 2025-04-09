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
    Replace all occurrences of:
      - %{var} with the repr() (string literal) of local_data[var],
      - @{var} with the repr() of global_data[var] (using dotted notation if needed),
      - ${...} with a string literal of the original placeholder (so it is preserved).
      
    The resulting expression (a valid Python expression as a string) is then ready to be
    eval'ed in a restricted environment.
    """
    # First, replace self-scope markers %{...} using local_data.
    pattern_local = re.compile(r'%{([^}]+)}')
    def repl_local(match):
        var_name = match.group(1).strip()
        value = local_data.get(var_name, match.group(0))
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return repr(unquote(value.value))
        elif isinstance(value, str):
            return repr(unquote(value))
        return str(value)
    expr = re.sub(pattern_local, repl_local, expr)

    # Next, replace global markers @{...} using global_data.
    pattern_global = re.compile(r'@{([^}]+)}')
    def repl_global(match):
        var_name = match.group(1).strip()
        if '.' in var_name:
            value = resolve_scoped_variable(var_name, global_data)
        else:
            value = global_data.get(var_name, match.group(0))
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return repr(unquote(value.value))
        elif isinstance(value, str):
            return repr(unquote(value))
        return str(value)
    expr = re.sub(pattern_global, repl_global, expr)

    # Finally, replace context markers ${...} with a quoted version (so they remain literals).
    pattern_context = re.compile(r'\$\{([^}]+)\}')
    def repl_context(match):
        placeholder = match.group(0)  # e.g. "${auth_token}"
        # Wrap the placeholder in repr to preserve it as a string literal.
        return repr(placeholder)
    expr = re.sub(pattern_context, repl_context, expr)

    return expr


def evaluate_f_string(f_str, global_data, local_data):
    """
    Evaluate an f-string by substituting interpolations.
    
    This function supports three kinds of markers:
      - Global markers: @{...} (looked up in global_data; supports dotted names)
      - Self/local markers: %{...} (looked up in local_data; supports dotted names)
      - Context markers: ${...} (looked up in global_data)
      
    f_str is assumed to start with f" or f'.
    """
    # Remove the leading f and surrounding quotes.
    inner = f_str[2:-1]

    # First pass: Process markers for global (@) and self/local (%) substitutions.
    pattern = re.compile(r'([@%]){([^}]+)}')

    def repl(match):
        scope_marker = match.group(1)
        var_name = match.group(2).strip()
        if scope_marker == '@':
            # Global lookup: if the name is dotted, do a nested lookup.
            if '.' in var_name:
                value = resolve_scoped_variable(var_name, global_data)
            else:
                value = global_data.get(var_name, match.group(0))
        elif scope_marker == '%':
            # Self/local lookup: use local_data.
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

    evaluated = re.sub(pattern, repl, inner)

    # Second pass: Process context markers of the form ${...} using the global_data.
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

    evaluated = re.sub(context_pattern, context_repl, evaluated)
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