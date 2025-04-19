"""
Folded‑expression evaluation for the *resolve* phase.

• Substitutes @{…} / %{…} immediately (supports dotted paths).
• Leaves ${…} placeholders for render‑time.
• Executes constant arithmetic / concatenation with safe_eval.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from lark import Token, Tree

from ._eval import safe_eval
from ._substitute import _substitute_vars  # still used for edge cases


# ───────────────────────────── token classes ──────────────────────────────
_STR_TOKENS = {
    "SINGLE_QUOTED_STRING",
    "TRIPLE_QUOTED_STRING",
    "TRIPLE_BACKTICK_STRING",
    "BACKTICK_STRING",
}

_SCOPE_PREFIX = {
    "GLOBAL_SCOPED_VAR": "@",
    "LOCAL_SCOPED_VAR":  "%",
    "CONTEXT_SCOPED_VAR": "$",
}


# ───────────────────────────── helpers ─────────────────────────────────────
def _lookup(path: str, *envs: Dict[str, Any]) -> Optional[Any]:
    """Return the first hit for a dotted path in the provided envs."""
    parts = path.split(".")
    for env in envs:
        cur: Any = env
        for p in parts:
            if not (isinstance(cur, dict) and p in cur):
                cur = None
                break
            cur = cur[p]
        if cur is not None:
            return cur
    return None


def _tok_to_py(
    tok: Token,
    g: Dict[str, Any],
    l: Dict[str, Any],
    c: Dict[str, Any],
) -> str:
    """Convert a Lark token to a Python snippet (or placeholder)."""
    if tok.type in _STR_TOKENS:
        raw = tok.value.strip('"\'`')
        return repr(raw)

    if tok.type in {"INTEGER", "FLOAT"}:
        return tok.value

    if tok.type == "BOOLEAN":
        return "True" if tok.value == "true" else "False"

    if tok.type == "OPERATOR":
        return tok.value

    if tok.type in _SCOPE_PREFIX:
        marker = _SCOPE_PREFIX[tok.type]
        inner = tok.value[2:-1]          # strip @{ … }

        if marker == "$":                # context – keep for render
            return tok.value

        val = (
            _lookup(inner, g) if marker == "@"
            else _lookup(inner, l, g)
        )
        if val is None:                  # unresolved – keep original text
            return tok.value

        if hasattr(val, "evaluate"):
            val = val.evaluate()
        if isinstance(val, str):
            val = val.strip('"\'')
        return repr(val)

    # default: return verbatim
    return tok.value


# ─────────────────────────── public entry‑point ───────────────────────────
def evaluate_expression_tree(
    tree: Tree,
    global_env: Dict[str, Any],
    local_env: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """Resolve a `<( … )>` expression as far as possible without context."""
    local_env = local_env or {}
    context = context or {}

    py_parts: List[str] = [
        _tok_to_py(tok, global_env, local_env, context)
        for tok in tree.scan_values(lambda v: isinstance(v, Token))
    ]
    py_expr = "".join(py_parts).strip()

    # ── fully static: evaluate completely ────────────────────────────────
    if "${" not in py_expr:
        try:
            return str(safe_eval(py_expr, local_env=local_env))
        except Exception:
            return py_expr

    # ── partially dynamic: replace ${…} with sentinel, eval rest ─────────
    SENTINEL = "__CTX_PLACEHOLDER__"
    tmp_expr = re.sub(r"\$\{[^}]+}", repr(SENTINEL), py_expr)

    try:
        interim = str(safe_eval(tmp_expr, local_env=local_env))
    except Exception:
        interim = py_expr

    # restore placeholders
    restored = interim.replace(SENTINEL, "${")
    # wrap so render() can finish substitution
    return f'f"{restored}"'


# ───────────────────── used by Config.render fallback ─────────────────────
def _render_folded_expression_node(
    node,
    env: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
):
    from ._ast_nodes import FoldedExpressionNode

    if isinstance(node, FoldedExpressionNode) and node.resolved is not None:
        return node.resolved
    return evaluate_expression_tree(node.content_tree, env, env, context)
