#!/usr/bin/env python3
"""
jaml/unparser.py

Re‑serialises an in‑memory config produced by the JAML parser back to text,
**preserving comments, inline‑comments, and comprehension‑based
table‑array headers**.

Highlights
----------
* Correctly emits `[[ … ]]` blocks (even when the header is a comprehension)
  instead of turning them into bogus assignments.
* Preserves every comment captured by the parser:
  * top‑level comments (`config_dict["__comments__"]`)
  * per‑section comments   (`section_dict["__comments__"]`)
  * inline comments wrapped in `ValueNode`.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from ._ast_nodes import (
    # “wrapper” nodes that keep original text
    SingleQuotedStringNode,
    TripleQuotedStringNode,
    BacktickStringNode,
    FStringNode,
    TripleBacktickStringNode,
    ValueNode,
    SingleLineArrayNode,
    MultiLineArrayNode,
    InlineTableNode,
    DictComprehensionNode,
    # table‑array helpers
    TableArrayHeaderNode,
    ComprehensionHeaderNode,
    TableArraySectionNode,
    # misc AST helpers
    StringExprNode,
    ComprehensionClausesNode,
    ComprehensionClauseNode,
    DottedExprNode,
    PairExprNode,
    AliasClauseNode,
    InClauseNode,
)


# --------------------------------------------------------------------------- #
# Main unparser
# --------------------------------------------------------------------------- #
class JMLUnparser:
    """Convert a parsed configuration back into DSL text."""

    # ------------------------------------------------------------------ #
    # ctor / utilities
    # ------------------------------------------------------------------ #
    def __init__(self, config: Any, debug: bool = False) -> None:
        self.config = config
        self.debug = debug
        if self.debug:
            print("[DEBUG] JMLUnparser initialised with", type(config))

    def _get_config_data(self) -> dict:
        """Extract a dict representation from common container shapes."""
        if isinstance(self.config, dict):
            return self.config
        for attr in ("data", "value", "to_dict", "__dict__"):
            if hasattr(self.config, attr):
                candidate = getattr(self.config, attr)
                return candidate() if callable(candidate) else candidate
        raise TypeError("Unsupported config container – cannot obtain mapping.")

    # ------------------------------------------------------------------ #
    # scalar / collection formatting
    # ------------------------------------------------------------------ #
    def format_value(self, val: Any) -> str:  # noqa: C901
        """Return *val* as DSL text, preserving wrappers and comments."""
        # ---------- wrappers ----------
        if isinstance(val, DictComprehensionNode):
            return val.origin
        if isinstance(val, ValueNode):
            return f"{self.format_value(val.value)}{val.comment or ''}"
        if isinstance(val, InlineTableNode):
            return (
                val.origin if "\n" not in val.origin else self._expand_inline_table(val)
            )
        if isinstance(val, (SingleLineArrayNode, MultiLineArrayNode)):
            return val.origin
        if isinstance(
            val,
            (
                SingleQuotedStringNode,
                TripleQuotedStringNode,
                BacktickStringNode,
                FStringNode,
                TripleBacktickStringNode,
            ),
        ):
            return val.origin

        # ---------- primitives ----------
        if isinstance(val, str):
            return f'"{val}"' if "\n" not in val else f'"""{val}"""'
        if isinstance(val, bool):
            return "true" if val else "false"
        if val is None:
            return "null"
        if isinstance(val, (int, float)):
            return str(val)

        # ---------- collections ----------
        if isinstance(val, list):
            return f"[{', '.join(self.format_value(v) for v in val)}]"
        if isinstance(val, dict):
            inner = ", ".join(f"{k} = {self.format_value(v)}" for k, v in val.items())
            return f"{{{inner}}}"

        # ---------- fallback ----------
        return str(val)

    # ------------------------------------------------------------------ #
    # inline‑table pretty printing (multiline)
    # ------------------------------------------------------------------ #
    def _expand_inline_table(self, tbl: InlineTableNode) -> str:
        text = tbl.origin.strip()
        inner = (
            text[1:-1].strip() if text.startswith("{") and text.endswith("}") else text
        )
        lines = [ln.rstrip(",").strip() for ln in inner.splitlines() if ln.strip()]
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # AST node -> text
    # ------------------------------------------------------------------ #
    def unparse_node(self, node: Any) -> str:  # noqa: C901
        """Turn helper AST nodes back into text."""
        # 1) full table‑array section
        if isinstance(node, TableArraySectionNode):
            header_txt = f"[[{self.unparse_node(node.header)}]]"
            body_lines: List[str] = []

            # comments stored on the node?
            if hasattr(node, "__comments__"):
                body_lines.extend(getattr(node, "__comments__"))  # type: ignore[arg-type]

            # children (assignments / subsections / stray comments)
            for child in node.body or []:
                if child is None:
                    continue
                if isinstance(child, str) and child.lstrip().startswith("#"):
                    body_lines.append(child)
                elif hasattr(child, "unparse"):
                    body_lines.append(child.unparse())  # type: ignore[attr-defined]
                else:
                    body_lines.append(self.unparse_node(child))

            return "\n".join([header_txt] + body_lines)

        # 2) header objects
        if isinstance(node, (TableArrayHeader, ComprehensionHeader)):
            return node.origin

        # 3) simple helpers
        if isinstance(node, StringExprNode):
            return node.origin
        if isinstance(node, DottedExprNode):
            return node.dotted_value
        if isinstance(node, PairExprNode):
            return f"{self.unparse_node(node.key)} = {self.unparse_node(node.value)}"
        if isinstance(node, (AliasClauseNode, InClauseNode)):
            return node.origin

        # 4) comprehension helpers
        if isinstance(node, ComprehensionClauseNode):
            vars_ = " ".join(self.unparse_node(v) for v in node.loop_vars)
            iterable = self.unparse_node(node.iterable)
            cond = (
                " if " + " ".join(self.unparse_node(c) for c in node.conditions)
                if node.conditions
                else ""
            )
            return f"for {vars_} in {iterable}{cond}"
        if isinstance(node, ComprehensionClausesNode):
            return " ".join(self.unparse_node(c) for c in node.clauses)

        # fallback
        return str(node)

    # ------------------------------------------------------------------ #
    # section helpers
    # ------------------------------------------------------------------ #
    def _collapse_section(self, path: List[Any], sect: Any) -> Tuple[List[str], Any]:
        str_path = [
            item.origin.strip("[]")
            if isinstance(item, (TableArrayHeaderNode, ComprehensionHeaderNode))
            else str(item)
            for item in path
        ]
        if isinstance(sect, dict) and len(sect) == 1:
            ((only_key, val),) = sect.items()
            if isinstance(val, dict) and not {"_value", "_annotation"} <= val.keys():
                return self._collapse_section(str_path + [only_key], val)
            if isinstance(val, InlineTableNode) and "\n" in val.origin:
                return str_path + [only_key], val
        return str_path, sect

    def _emit_section(
        self,
        sect: Any,
        path: List[str],
    ) -> str:
        """Serialise a `[section]` (or collapsed inline‑table)."""
        # inline‑table collapsed leaf
        if not isinstance(sect, dict):
            header = f"[{'.'.join(path)}]"
            return f"{header}\n{self._expand_inline_table(sect)}\n"

        lines: List[str] = [f"[{'.'.join(path)}]"]

        # comments inside the section
        for cmt in sect.get("__comments__", []):
            lines.append(cmt)

        # assignments
        for k, v in sect.items():
            if k == "__comments__":
                continue
            if isinstance(v, dict) and {"_value", "_annotation"} <= v.keys():
                print("+++==>", k, v, type(k), type(v))
                val_txt = self.format_value(v["_value"])
                lines.append(f"{k}: {v['_annotation']} = {val_txt}")
            elif not isinstance(v, dict):
                if isinstance(k, TableArrayHeader):
                    print("====>", k, v, type(k), type(v))
                    lines.append(f"[[{k}]]")
                elif isinstance(k, TableArraySectionNode):
                    print("====>", k, v, type(k), type(v))
                    lines.append(f"[[{k}]]")
                else:
                    print("==>", k, v, type(k), type(v))
                    lines.append(f"{k} = {self.format_value(v)}")

        if len(lines) > 1:
            lines.append("")  # blank line before subsections

        # nested subsections
        for k, v in sect.items():
            if isinstance(v, dict):
                print("---->", k, v, type(k), type(v))
                sub_path, collapsed = self._collapse_section(path + [k], v)
                lines.append(self._emit_section(collapsed, sub_path))

        return "\n".join(lines).rstrip("\n")

    def _emit_section(self, sect: Any, path: List[Any]) -> str:
        # Convert path elements to strings
        str_path = []
        for item in path:
            if isinstance(item, (TableArrayHeaderNode, ComprehensionHeaderNode)):
                str_path.append(
                    item.origin.strip("[]") if hasattr(item, "origin") else str(item)
                )
            else:
                str_path.append(str(item))
        if not isinstance(sect, dict):
            header = f"[{'.'.join(str_path)}]"
            return f"{header}\n{self._expand_inline_table(sect)}\n"
        lines: List[str] = [f"[{'.'.join(str_path)}]"]
        for cmt in sect.get("__comments__", []):
            lines.append(cmt)
        for k, v in sect.items():
            if k == "__comments__":
                continue
            if isinstance(v, dict) and {"_value", "_annotation"} <= v.keys():
                val_txt = self.format_value(v["_value"])
                lines.append(f"{k}: {v['_annotation']} = {val_txt}")
            elif not isinstance(v, dict):
                lines.append(f"{k} = {self.format_value(v)}")
        if len(lines) > 1:
            lines.append("")
        for k, v in sect.items():
            if isinstance(v, dict) and not {"_value", "_annotation"} <= v.keys():
                sub_path, collapsed = self._collapse_section([k], v)
                lines.append(self._emit_section(collapsed, str_path + sub_path))
        return "\n".join(lines).rstrip("\n")

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def unparse(self):
        out: List[str] = []
        data = self._get_config_data()
        for cmt in data.get("__comments__", []):
            out.append(cmt)
        if data.get("__comments__"):
            out.append("")
        for key, value in data.items():
            if key == "__comments__":
                continue
            if isinstance(value, list) and all(
                isinstance(v, (dict, TableArraySectionNode)) for v in value
            ):
                for section in value:
                    if isinstance(section, TableArraySectionNode):
                        out.append(self.unparse_node(section))
                    else:
                        key_str = (
                            key.origin.strip("[]")
                            if isinstance(
                                key, (TableArrayHeaderNode, ComprehensionHeaderNode)
                            )
                            else key
                        )
                        lines = [f"[[{key_str}]]"]
                        for k, v in section.items():
                            if (
                                isinstance(v, dict)
                                and {"_value", "_annotation"} <= v.keys()
                            ):
                                lines.append(
                                    f"{k}: {v['_annotation']} = {self.format_value(v['_value'])}"
                                )
                            else:
                                lines.append(f"{k} = {self.format_value(v)}")
                        out.append("\n".join(lines))
                out.append("")
                continue
            if isinstance(value, dict):
                path, collapsed = self._collapse_section([key], value)
                out.append(self._emit_section(collapsed, path))
                out.append("")
                continue
            rhs = (
                self.format_value(value)
                if not hasattr(value, "unparse")
                else value.unparse()
            )
            out.append(f"{key} = {rhs}")
        return "\n".join(out).rstrip("\n")

    # Convenience
    def __str__(self) -> str:  # pragma: no cover
        return self.unparse()
