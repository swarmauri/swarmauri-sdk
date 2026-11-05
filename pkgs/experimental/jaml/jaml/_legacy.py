"""Render the deferred expression syntax supported by the original JAML API."""

from __future__ import annotations

import ast
import json
import re

from ._eval import safe_eval

EXPRESSION = (
    r"~(?:\((?:[^()]|\([^()]*\))*\)|\[(?:[^\[\]]|\[[^\[\]]*\])*\])|\{\^.*?\^\}"
)
QUOTED = r'''""".*?"""|\x27\x27\x27.*?\x27\x27\x27|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27'''
SCOPED = r"([@$%])(?:\{([^}]+)\}|([A-Za-z_]\w*(?:\.\w+)*))"


def _lookup(path, *environments):
    for environment in environments:
        value = environment
        for part in path.split("."):
            if not isinstance(value, dict) or part not in value:
                break
            value = value[part]
        else:
            return value
    raise KeyError(path)


def _literal(value):
    if isinstance(value, dict):
        return (
            "{"
            + ", ".join(f"{k} = {_literal(v)}" for k, v in value.items())
            + "}"
        )
    return json.dumps(value, ensure_ascii=False)


class _StringConcatenation(ast.NodeTransformer):
    def visit_BinOp(self, node):
        node = self.generic_visit(node)
        if (
            isinstance(node.op, ast.Add)
            and isinstance(node.left, ast.Constant)
            and isinstance(node.right, ast.Constant)
            and (
                isinstance(node.left.value, str)
                or isinstance(node.right.value, str)
            )
        ):
            return ast.copy_location(
                ast.Constant(str(node.left.value) + str(node.right.value)),
                node,
            )
        return node


def render_source(source, context, globals):
    """Replace deferred expressions without discarding annotations or layout."""
    tokens = re.compile(f"(?:{QUOTED})|(?:{EXPRESSION})", re.S)
    references = re.compile(f"(?:{QUOTED})|(?:{SCOPED})", re.S)

    def replace_expression(match):
        raw = match.group()
        if not raw.startswith(("~", "{^")):
            return raw
        headers = list(
            re.finditer(r"^\s*\[([^\[\]\n]+)\]", source[: match.start()], re.M)
        )
        local = _lookup(headers[-1][1], globals) if headers else globals

        def replace_reference(reference):
            marker, braced, dotted = reference.groups()
            if marker is None:
                return reference.group()
            environments = (
                (context,) if marker == "$" else (local, globals, context)
            )
            return repr(_lookup(braced or dotted, *environments))

        inner = raw[2:-2] if raw.startswith("{^") else raw[1:]
        expression = references.sub(replace_reference, inner).strip()
        tree = _StringConcatenation().visit(ast.parse(expression, mode="eval"))
        value = safe_eval(ast.unparse(ast.fix_missing_locations(tree)), {})
        return _literal(value)

    return tokens.sub(replace_expression, source)
