from collections.abc import MutableMapping
from typing import Any, Dict, IO, Optional

from ._fstring import _evaluate_f_string


class Config(MutableMapping):
    """
    A thin wrapper around the parsed AST that preserves round‑trip fidelity
    yet behaves like a normal mutable mapping.

    • `resolve()` collapses every AST node and expands **static** f‑strings
      (those that do *not* reference `${…}` context placeholders).

    • `render()` finishes the job, expanding any remaining f‑strings with the
      runtime *context* supplied by the caller.
    """

    # imported lazily to avoid circulars
    from ._ast_nodes import StartNode

    # ───────────────────────────────────────────────────────── basics
    def __init__(self, ast: "Config.StartNode"):
        self._ast   = ast                 # top‑level StartNode
        self._data  = ast.data            # raw underlying dict
        print("[DEBUG CONFIG INIT]:", self._data, self._ast)

    # mapping protocol --------------------------------------------------------
    def __getitem__(self, key: str) -> Any:
        """
        Return the **raw** value from the underlying data mapping,
        without performing any f‑string evaluation.
        """
        cur = self._data
        for part in key.split("."):
            cur = cur[part]
        return cur

    def __setitem__(self, key: str, value: Any):
        # 1) update the *plain* data dict
        cur   = self._data
        parts = key.split(".")
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value

        # 2) update the AST + refresh any dependent concat expressions
        self._sync_ast(key, value)

    def __delitem__(self, key: str):
        cur   = self._data
        parts = key.split(".")
        for part in parts[:-1]:
            cur = cur[part]
        del cur[parts[-1]]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Config({self._data})"

    def __contains__(self, key: str) -> bool:
        """
        Check membership against the raw, un‑resolved data mapping so that
        conditional‑header strings remain present until resolve() is called.
        """
        # Direct key match
        if key in self._data:
            return True
        # Fallback: normalize whitespace for approximate match of dynamic section keys
        import re
        def _normalize(s: str) -> str:
            # collapse all whitespace (spaces, newlines, tabs) to single spaces and trim
            return re.sub(r"\s+", " ", s.strip())
        normalized_key = _normalize(key)
        for existing in self._data:
            if isinstance(existing, str) and _normalize(existing) == normalized_key:
                return True
        return False

    # ──────────────────────────────────────────────────────── helpers
    def _sync_ast(self, dotted: str, value: Any):
        """
        Bring the underlying AST in line with a mutation to the Config
        mapping interface.

        • `dotted`  – key in dotted‑path form, e.g. "server.port"
        • `value`   – new Python value assigned by the user
        """
        from ._ast_nodes import AssignmentNode, SingleQuotedStringNode

        # 1) update the raw data cache held by the root StartNode
        cur = self._ast.data
        for part in dotted.split(".")[:-1]:
            cur = cur.setdefault(part, {})
        cur[dotted.split(".")[-1]] = value

        # 2) walk the top‑level line list to find the matching AssignmentNode
        for node in self._ast.lines:
            if isinstance(node, AssignmentNode) and node.identifier.value == dotted:
                # Wrap plain scalars so .emit() round‑trips exactly
                if isinstance(value, str):
                    sq = SingleQuotedStringNode()
                    # ensure the literal keeps its quotes for fidelity
                    sq.value  = f'"{value}"' if not (value.startswith('"') or value.startswith("'")) else value
                    sq.origin = sq.value
                    node.value = sq
                else:
                    node.value = value  # complex objects (dicts, lists, etc.)
                node.resolved = value
                break

    # round‑trip helpers ------------------------------------------------------
    def dumps(self) -> str:
        """Emit the configuration exactly as it would appear on disk."""
        return self._ast.emit()

    dump = staticmethod(lambda obj, fp: fp.write(Config.dumps(obj)))  # type: ignore

    # ───────────────────────────────────────────────────────── resolution
    def resolve(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # ──────────────────────────────────────────────────────────────
        # ① expand global- and local-scope f-strings
        def _eval_fstrings(mapping: Dict[str, Any]):
            for key, val in list(mapping.items()):
                if isinstance(val, str) and (val.startswith('f"') or val.startswith("f'")):
                    # Skip context-scoped placeholders (${...}), only expand static f-strings
                    if '${' not in val:
                        mapping[key] = _evaluate_f_string(
                            val,
                            global_data=self._data,
                            local_data=mapping,
                            context={},
                        )
                elif isinstance(val, dict):
                    _eval_fstrings(val)
        _eval_fstrings(self._data)

        from ._ast_nodes import BaseNode, SectionNode, TableArraySectionNode, TableArrayHeaderNode
        # ──────────────────────────────────────────────────────────────
        import re
        # ② expand conditional headers (unchanged)
        for node in list(self._ast.lines):
            if isinstance(node, SectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr = node.header.origin

                def _scoped_repl(m):
                    var = m.group(1)
                    return repr(self._data.get(var)) if var in self._data else "None"

                expr_py = re.sub(r'[@%]\{([^}]+)\}', _scoped_repl, expr)
                expr_py = expr_py.replace('null', 'None')
                try:
                    result = eval(expr_py, {}, {})
                except Exception:
                    continue

                if not result:
                    self._data.pop(raw_key, None)
                else:
                    section_map = self._data.pop(raw_key, None)
                    self._data[result] = section_map
                    node.header.value = result
                    node.header.origin = result

            if isinstance(node, TableArraySectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr = node.header.origin

                def _scoped_repl(m):
                    var = m.group(1)
                    return repr(self._data.get(var)) if var in self._data else "None"

                expr_py = re.sub(r'[@%]\{([^}]+)\}', _scoped_repl, expr)
                expr_py = expr_py.replace('null', 'None')
                try:
                    result = eval(expr_py, {}, {})
                except Exception:
                    continue

                if not result:
                    self._data.pop(raw_key, None)
                else:
                    section_map = self._data.pop(raw_key, None)
                    self._data[result] = section_map
                    node.header.value = result
                    node.header.origin = result

        # ──────────────────────────────────────────────────────────────
        def _collapse(value: Any, scope: Dict[str, Any]) -> Any:
            from ._ast_nodes import BaseNode

            if isinstance(value, BaseNode):
                value.resolve(self._data, scope)
                return _collapse(value.evaluate(), scope)

            if isinstance(value, dict):
                merged = {**scope, **value}
                out: Dict[str, Any] = {}
                for k, v in value.items():
                    if k == "__comments__":
                        out[k] = v
                    else:
                        out[k] = _collapse(v, merged)
                return out

            if isinstance(value, list):
                return [_collapse(x, scope) for x in value]

            return value

        collapsed: Dict[str, Any] = {}
        for key, val in list(self._data.items()):
            if key == "__comments__":
                collapsed[key] = val
                continue
            collapsed[key] = _collapse(val, self._data)

        # ──────────────────────────────────────────────────────────────
        # ③ post-process both global- and local-scoped placeholders in strings
        def _expand(val: Any, local_scope: Any) -> Any:
            import re
            if isinstance(val, dict):
                return {k: _expand(v, val) for k, v in val.items()}
            if isinstance(val, str):
                pattern = re.compile(r'%\{([^}]+)\}')
                def repl(m):
                    path = m.group(1)
                    tgt = local_scope
                    for part in path.split('.'):
                        if isinstance(tgt, dict) and part in tgt:
                            tgt = tgt[part]
                        else:
                            return m.group(0)
                    return str(tgt)
                return pattern.sub(repl, val)
            return val

        out = {k: _expand(v, v if isinstance(v, dict) else collapsed) for k, v in collapsed.items()}
        return out




    # ──────────────────────────────────────────── render
    def render(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Finish expanding f-strings and scoped placeholders using the provided context,
        returning a fully-resolved mapping.
        """
        from ._fstring import _evaluate_f_string
        from ._ast_nodes import (
            SectionNode,
            TableArraySectionNode,
            ComprehensionHeaderNode,
            TableArrayHeaderNode,
            AssignmentNode,
        )
        import re

        context = context or {}
        print("[DEBUG _config.render] Entering render with context:", context)
        print("[DEBUG _config.render] Initial data keys:", list(self._data.keys()))

        # ❶ expand table-array comprehensions
        for idx, node in enumerate(list(self._ast.lines)):
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, ComprehensionHeaderNode):
                hdr = node.header
                hdr.render(self._data, {}, context)
                produced: Dict[str, Dict] = {}
                new_nodes: List[TableArraySectionNode] = []
                original_lines = self._ast.lines
                pos = original_lines.index(node)
                for hdr_name, alias_env in hdr.header_envs:
                    entry: Dict[str, Any] = {}
                    for item in node.body:
                        if isinstance(item, AssignmentNode):
                            item.resolve(self._data, alias_env, context)
                            entry[item.identifier.value] = item.evaluate()
                    produced[hdr_name] = entry
                    static = TableArraySectionNode()
                    static.header = TableArrayHeaderNode()
                    static.header.origin = hdr_name
                    static.header.value = hdr_name
                    static.body = node.body
                    new_nodes.append(static)
                original_lines[pos:pos+1] = new_nodes
                for hdr_name, entry in produced.items():
                    parts = hdr_name.split('.')
                    cur = self._data
                    for p in parts[:-1]:
                        cur = cur.setdefault(p, {})
                    cur[parts[-1]] = entry
                self._data.pop(hdr.origin, None)

        # ❷ expand conditional headers (with context)
        def _expand_conditional_headers():
            for node in list(self._ast.lines):
                if isinstance(node, SectionNode) and isinstance(node.header, TableArrayHeaderNode):
                    raw = node.header.origin
                    def repl(m): return repr(context.get(m.group(1), self._data.get(m.group(1))))
                    expr_py = re.sub(r"\$\{([^}]+)\}", repl, raw).replace('null','None')
                    try:
                        result = eval(expr_py, {}, {})
                    except Exception:
                        continue
                    if not result:
                        self._data.pop(node.header.value, None)
                    else:
                        section_map = self._data.pop(node.header.value, None)
                        node.header.value = result
                        node.header.origin = result
                        self._data[result] = section_map
        _expand_conditional_headers()

        # ❸ collapse AST nodes into Python values
        def _collapse(val: Any, scope: Dict[str, Any]) -> Any:
            from ._ast_nodes import BaseNode
            if isinstance(val, BaseNode):
                val.resolve(self._data, scope, context)
                return _collapse(val.evaluate(), {**scope, **(val.evaluate() if isinstance(val.evaluate(), dict) else {})})
            if isinstance(val, dict):
                merged = {**scope, **val}
                return {k: _collapse(v, merged) for k, v in val.items()}
            if isinstance(val, list):
                return [_collapse(x, scope) for x in val]
            return val

        collapsed: Dict[str, Any] = {}
        for key, val in list(self._data.items()):
            if key == '__comments__':
                collapsed[key] = val
            else:
                collapsed[key] = _collapse(val, self._data)
                self._data[key] = collapsed[key]

        # ❹ expand remaining f-strings using context
        def _eval_context_fstrings(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _eval_context_fstrings(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_eval_context_fstrings(v) for v in obj]
            if isinstance(obj, str) and (obj.startswith('f"') or obj.startswith("f'")):
                try:
                    return _evaluate_f_string(obj, global_data=self._data, local_data={}, context=context)
                except Exception:
                    return obj
            return obj

        return _eval_context_fstrings(collapsed)

