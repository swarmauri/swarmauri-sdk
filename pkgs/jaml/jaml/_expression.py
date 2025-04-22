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
    # ──────────────────────────────── Strings ────────────────────────────────
    if tok.type in _STR_TOKENS:
        raw = tok.value
        # If the first and last chars are matching quotes/backticks, strip them
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'", "`"):
            raw = raw[1:-1]
        return repr(raw)

    # ───────────────────────────── Numerics & Booleans ─────────────────────────
    if tok.type in {"INTEGER", "FLOAT"}:
        return tok.value
    if tok.type == "BOOLEAN":
        return "True" if tok.value == "true" else "False"

    # ───────────────────────────── Operators ────────────────────────────────
    if tok.type == "OPERATOR":
        return tok.value

    # ───────────────────────── Scope‑prefixed vars ───────────────────────────
    if tok.type in _SCOPE_PREFIX:
        marker = _SCOPE_PREFIX[tok.type]
        inner  = tok.value[2:-1]  # strip the @{…}, %{…}, or ${…}

        # Context‑scoped (${…})
        if marker == "$":
            ctx = c or {}
            val = _lookup(inner, ctx)
            if val is not None:
                if hasattr(val, "evaluate"):
                    val = val.evaluate()
                return repr(val)
            return tok.value

        # Global (@{…}) or local (%{…})
        val = (_lookup(inner, g) if marker == "@" else _lookup(inner, l, g))
        if val is None:
            return tok.value
        if hasattr(val, "evaluate"):
            val = val.evaluate()
        if isinstance(val, str):
            # strip any leftover quotes
            val = val.strip('"\'' )
        return repr(val)

    # ────────────────────────────── Fallback ────────────────────────────────
    return tok.value





# ─────────────────────────── public entry‑point ───────────────────────────
def evaluate_expression_tree(
    tree: Tree,
    global_env: Dict[str, Any],
    local_env: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """Resolve a `<( … )>` expression, substituting @{…} and %{…} immediately.
    Leaves ${…} intact and wraps in an f‑string if any remain."""
    import re
    from ._eval import safe_eval
    from lark import Token
    from ._ast_nodes import BaseNode, HspacesNode, InlineWhitespaceNode, WhitespaceNode

    # Debug entry
    print("[DEBUG EXPR] → evaluate_expression_tree called")
    local_env = local_env or {}
    context = context or {}
    print(f"[DEBUG EXPR] Global env: {global_env}")
    print(f"[DEBUG EXPR] Local env:  {local_env}")
    print(f"[DEBUG EXPR] Context:    {context}")

    # Collect only meaningful children (drop whitespace tokens/nodes)
    items = [
        c for c in getattr(tree, 'children', [])
        if not (
            (isinstance(c, Token) and c.type in ("HSPACES", "INLINE_WS", "WHITESPACE"))
            or isinstance(c, (HspacesNode, InlineWhitespaceNode, WhitespaceNode))
        )
    ]
    print(f"[DEBUG EXPR] Expression items: {[getattr(c, 'value', repr(c)) for c in items]}")

    parts: List[str] = []
    for c in items:
        if isinstance(c, Token):
            snippet = _tok_to_py(c, global_env, local_env, context)
        elif isinstance(c, BaseNode) and hasattr(c, 'meta') and isinstance(c.meta, Token):
            snippet = _tok_to_py(c.meta, global_env, local_env, context)
        elif isinstance(c, BaseNode):
            try:
                c.resolve(global_env, local_env, context)
            except Exception:
                pass
            val = getattr(c, 'resolved', None) or getattr(c, 'value', None)
            if isinstance(val, str):
                snippet = repr(val.strip('"\''))
            else:
                snippet = str(val)
        else:
            snippet = str(c)
        parts.append(snippet)
        print(f"[DEBUG EXPR] Part snippet: {snippet}")

    # Build py_expr by direct concatenation (preserve '+' tokens from parts)
    py_expr = ''.join(parts)
    print(f"[DEBUG EXPR] Built py_expr: {py_expr}")

    # Static-only: no ${…}, so safe_eval
    if "${" not in py_expr:
        try:
            result = str(safe_eval(py_expr, local_env=local_env))
            print(f"[DEBUG EXPR] Static eval result: {result}")
            return result
        except Exception as e:
            print(f"[DEBUG EXPR] Static eval error: {e}")
            return py_expr

        # Mixed dynamic: preserve ${…}
    # Find the first placeholder index
    placeholder_idxs = [idx for idx, part in enumerate(parts) if isinstance(part, str) and part.startswith('${')]
    if placeholder_idxs:
        i0 = placeholder_idxs[0]
        # Exclude the trailing '+' before placeholder if present
        if i0 > 0 and parts[i0-1] == '+':
            static_parts = parts[:i0-1]
        else:
            static_parts = parts[:i0]
        placeholder_text = parts[i0]
        # Evaluate only the static prefix
        static_expr = ''.join(static_parts)
        try:
            static_value = str(safe_eval(static_expr, local_env=local_env))
        except Exception as e:
            print(f"[DEBUG EXPR] Static prefix eval error: {e}")
            static_value = static_expr
        # Build final f-string with placeholder
        f_res = f'f"{static_value}{placeholder_text}"'
        print(f"[DEBUG EXPR] Final f-string result: {f_res}")
        return f_res
    else:
        # No placeholders detected, fallback
        return py_expr




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
