"""
_resolve.py

Handles global/local references, folded expressions, and partial evaluation. 
"""

from typing import Dict, Any
from copy import deepcopy
import re

from .lark_nodes import PreservedString, DeferredComprehension, FoldedExpressionNode

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
    elif isinstance(node, DeferredComprehension):
        return node.evaluate(global_env)
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

def _maybe_resolve_fstring(fstring_literal: str, global_env: Dict[str, Any],
                           local_env: Dict[str, Any]) -> str:
    if _has_dynamic_placeholder(fstring_literal):
        return fstring_literal
    # strip leading f
    inner = fstring_literal.lstrip()[1:]
    if inner.startswith('"') or inner.startswith("'"):
        inner = inner[1:-1]
    return _substitute_vars(inner, global_env, local_env)

def _resolve_folded_expression_node(node, global_env, local_env) -> str:
    """
    For a FoldedExpressionNode, parse out the inside text, do partial substitution
    for @{} / %{} references, but keep ${} placeholders.
    """
    folded_literal = node.original
    # e.g. <( "http://" + @{server.host} + ... )>
    stripped = folded_literal.strip()
    if not (stripped.startswith("<(") and stripped.endswith(")>")):
        return folded_literal  # fallback or partial
    inner = stripped[2:-2].strip()

    # split on '+' at top-level
    parts = [p.strip() for p in inner.split('+')]
    resolved_parts = []
    for part in parts:
        # if part is a quoted literal
        if (part.startswith('"') and part.endswith('"')) or (part.startswith("'") and part.endswith("'")):
            # remove the quotes
            resolved_parts.append(part[1:-1])
        else:
            # static substitution
            substituted = _substitute_vars(part, global_env, local_env)
            resolved_parts.append(substituted)
    final_str = "".join(resolved_parts)
    return final_str

def _has_dynamic_placeholder(s: str) -> bool:
    return bool(re.search(r"\$\{\s*[^}]+\}", s))

def _substitute_vars(expr: str, global_env: Dict[str, Any], local_env: Dict[str, Any]) -> str:
    # local references: %{var}
    def repl_local(m):
        var = m.group(1).strip()
        if local_env and var in local_env:
            return str(local_env[var])
        return f"%{{{var}}}"
    tmp = re.sub(r'%\{([^}]+)\}', repl_local, expr)

    # global references: @{var} or dotted
    def repl_global(m):
        var = m.group(1).strip()
        if '.' in var:
            # e.g. path.base
            section, key = var.split('.', 1)
            sect_val = global_env.get(section)
            if isinstance(sect_val, dict) and key in sect_val:
                return str(sect_val[key])
        if var in global_env:
            return str(global_env[var])
        return f"@{{{var}}}"
    replaced = re.sub(r'@\{([^}]+)\}', repl_global, tmp)
    return replaced

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
