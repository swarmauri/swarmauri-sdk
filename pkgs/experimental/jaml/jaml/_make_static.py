# jaml/_helpers.py  (new small util module)
from __future__ import annotations
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ._ast_nodes import TableArraySectionNode, SectionNode


def make_static_table_array(header_str: str, scope: Dict) -> "TableArraySectionNode":
    from ._ast_nodes import TableArraySectionNode, TableArrayHeaderNode

    ta = TableArraySectionNode()
    ta.header = TableArrayHeaderNode(origin=header_str, value=header_str)
    ta.body = []  # no inline assignments in the header-only form
    ta.value = scope
    return ta


def make_static_section(header: str, scope: Dict) -> "SectionNode":
    from ._ast_nodes import (
        SectionNode,
        SectionNameNode,
        AssignmentNode,
        SingleQuotedStringNode,
        IntegerNode,
        FloatNode,
        BooleanNode,
        NullNode,
    )

    """
    Build a *static* SectionNode (no comprehensions) from a header string
    and a dict of key‑value pairs that are already evaluated.
    """
    sec = SectionNode()

    # header
    sn = SectionNameNode()
    sn.parts = [type("Tok", (), {"value": header})]  # fake IDENTIFIER token
    sn.value = header
    sn.origin = header
    sec.header = sn
    sec.lbrack = type("Tok", (), {"value": "["})
    sec.rbrack = type("Tok", (), {"value": "]"})

    # body lines
    for k, v in scope.items():
        a = AssignmentNode()
        tok_id = type("Tok", (), {"value": k})
        a.identifier = tok_id
        a.equals = type("Tok", (), {"value": "="})

        def wrap_scalar(val):
            if isinstance(val, str):
                s = SingleQuotedStringNode()
                s.value = val
                s.origin = f'"{val}"'
                return s
            if isinstance(val, bool):
                b = BooleanNode()
                b.value = "true" if val else "false"
                b.resolved = val
                return b
            if isinstance(val, int):
                n = IntegerNode()
                n.value = str(val)
                n.resolved = val
                return n
            if isinstance(val, float):
                f = FloatNode()
                f.value = str(val)
                f.resolved = val
                return f
            if val is None:
                n = NullNode()
                n.value = "null"
                return n
            return val  # already a node or complex obj

        a.value = wrap_scalar(v)
        a.resolved = v
        sec.contents.append(a)

    return sec
