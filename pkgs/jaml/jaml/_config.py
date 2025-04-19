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
        Return the resolved value at `key`, interpreting inline tables,
        concatenations, scoped vars, etc., so that nested lookups
        like config["test"]["module"]["name"] yield plain Python values.
        """
        # Produce a fully resolved plain dict
        resolved = self.resolve()
        cur = resolved
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
        """
        Fully collapse the raw AST into a plain Python mapping, resolving every
        node that **does not** depend on per‑call *context*.

        Resolution order for placeholders and scoped variables:

        1. *context*                – values supplied by the caller
        2. current local scope      – earlier keys in the same mapping
        3. full configuration root  – the whole config file

        Any placeholder still unresolved after those three passes is left
        untouched so that a later `render()` call can inject a runtime context.
        """
        from ._ast_nodes import BaseNode, SectionNode, TableArraySectionNode, TableArrayHeaderNode

        context = context or {}

        # ────────────────────────────────────────────────── ❶ expand conditional headers
        import re
        for node in list(self._ast.lines):
            # ─ conditional single-bracket section headers ──────────────
            if isinstance(node, SectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr    = node.header.origin

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
                    node.header.value  = result
                    node.header.origin = result

            # ─ conditional table‑array section headers ────────────────
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr    = node.header.origin

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
                    node.header.value  = result
                    node.header.origin = result

        # ──── collapse helpers ───────────────────────────────────────
        def _collapse(value: Any, scope: Dict[str, Any]) -> Any:
            from ._ast_nodes import BaseNode

            if isinstance(value, BaseNode):
                value.resolve(self._data, scope, context)
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

        # … rest of resolve stays unchanged …

        collapsed: Dict[str, Any] = {}
        # Snapshot so mutations don’t break iteration
        for key, val in list(self._data.items()):
            if key == "__comments__":
                collapsed[key] = val
                continue
            collapsed[key] = _collapse(val, self._data)

        # ────────────────────────────────────────────────── post‑process scoped‑string patterns
        _PAT = re.compile(r'%\{([^}]+)\}(.*)')

        def _expand(val: Any) -> Any:
            if isinstance(val, dict):
                return {k: _expand(v) for k, v in val.items()}
            if isinstance(val, str):
                m = _PAT.fullmatch(val)
                if m:
                    path, rest = m.groups()
                    tgt: Any = collapsed
                    for part in path.split('.'):
                        if isinstance(tgt, dict) and part in tgt:
                            tgt = tgt[part]
                        else:
                            tgt = None
                            break
                    if tgt is not None:
                        return str(tgt) + rest
                return val
            return val

        return _expand(collapsed)


    # ──────────────────────────────────────────── render
    def render(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fully materialise the configuration, expanding:

        • ${placeholders}                           – using *context*
        • scoped variables %{…}/@{…}                – using current scope
        • concat-expressions & f-strings
        • *comprehension sections*                  – [[for x in …]] and [for x in …]
        • *conditional headers*                     – ["name" if … else null]
        """
        from ._ast_nodes import (
            BaseNode,
            SectionNode,
            TableArraySectionNode,
            ComprehensionHeaderNode,
            TableArrayHeaderNode,
            AssignmentNode,
            SingleQuotedStringNode,
        )

        context = context or {}

        # ────────────────────────────────── ❶ expand all comprehension sections
        for node in list(self._ast.lines):
            # single-bracket comprehension → SectionNode
            if isinstance(node, SectionNode) and isinstance(node.header, ComprehensionHeaderNode):
                raw_key = node.header.value
                node.render(self._data, context)
                self._data.pop(raw_key, None)

            # table-array comprehension → TableArraySectionNode
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, ComprehensionHeaderNode):
                raw_key = node.header.value
                node.header.render(self._data, {}, context)
                produced: Dict[str, Dict] = {}
                new_nodes: List[TableArraySectionNode] = []
                lines = self._ast.lines
                idx = lines.index(node)

                # collect entries and build static AST nodes
                for hdr, alias_env in node.header.header_envs:
                    entry: Dict[str, Any] = {}
                    for item in node.body:
                        if isinstance(item, AssignmentNode):
                            item.resolve(self._data, alias_env, context)
                            entry[item.identifier.value] = item.evaluate()
                    produced[hdr] = entry
                    hdr_node = TableArrayHeaderNode()
                    hdr_node.origin = hdr
                    hdr_node.value = hdr
                    static_node = TableArraySectionNode()
                    static_node.header = hdr_node
                    static_node.body = node.body
                    new_nodes.append(static_node)

                # splice the concrete sections into the AST
                lines[idx: idx + 1] = new_nodes

                # insert produced entries into nested mapping
                for hdr_str, entry_dict in produced.items():
                    parts = hdr_str.split('.')
                    cur = self._data
                    for part in parts[:-1]:
                        cur = cur.setdefault(part, {})
                    cur[parts[-1]] = entry_dict

                # remove the placeholder key
                self._data.pop(raw_key, None)

        # ────────────────────────────────── ❷ expand conditional headers
        import re
        for node in list(self._ast.lines):
            # conditional single-bracket section headers
            if isinstance(node, SectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr = node.header.origin

                def _repl(m):
                    var = m.group(1)
                    val = context.get(var, self._data.get(var))
                    return repr(val)

                expr_py = re.sub(r'\$\{([^}]+)\}', _repl, expr)
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

            # conditional table-array section headers
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr = node.header.origin

                def _repl(m):
                    var = m.group(1)
                    val = context.get(var, self._data.get(var))
                    return repr(val)

                expr_py = re.sub(r'\$\{([^}]+)\}', _repl, expr)
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

        # ────────────────────────────────── ❸ collapse & build final mapping
        def _collapse(val: Any, scope: Dict[str, Any]) -> Any:
            from ._ast_nodes import BaseNode

            if isinstance(val, BaseNode):
                val.resolve(self._data, scope, context)
                return _collapse(val.evaluate(), scope)
            if isinstance(val, dict):
                merged = {**scope, **val}
                return {k: _collapse(v, merged) for k, v in val.items()}
            if isinstance(val, list):
                return [_collapse(x, scope) for x in val]
            return val

        final: Dict[str, Any] = {}
        for k, v in list(self._data.items()):
            if k == "__comments__":
                final[k] = v
            else:
                final[k] = _collapse(v, self._data)
                self._data[k] = final[k]

        return final


        
        """
        Fully materialise the configuration, expanding:

        • ${placeholders}                           – using *context*
        • scoped variables %{…}/@{…}                – using current scope
        • concat-expressions & f-strings
        • *comprehension sections*                  – [[for x in …]] and [for x in …]
        • *conditional headers*                     – ["name" if … else null]
        """
        from ._ast_nodes import (
            BaseNode,
            SectionNode,
            TableArraySectionNode,
            ComprehensionHeaderNode,
            TableArrayHeaderNode,
            AssignmentNode,
            SingleQuotedStringNode,
        )

        context = context or {}

        # ────────────────────────────────── ❶ expand all comprehension sections
        for node in list(self._ast.lines):
            # single-bracket comprehension → SectionNode
            if isinstance(node, SectionNode) and isinstance(node.header, ComprehensionHeaderNode):
                raw_key = node.header.value
                node.render(self._data, context)
                self._data.pop(raw_key, None)

            # table-array comprehension → TableArraySectionNode
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, ComprehensionHeaderNode):
                raw_key = node.header.value
                node.header.render(self._data, {}, context)
                produced: Dict[str, Dict] = {}
                new_nodes: List[TableArraySectionNode] = []
                lines = self._ast.lines
                idx = lines.index(node)

                for hdr, alias_env in node.header.header_envs:
                    entry: Dict[str, Any] = {}
                    for item in node.body:
                        if isinstance(item, AssignmentNode):
                            item.resolve(self._data, alias_env, context)
                            entry[item.identifier.value] = item.evaluate()
                    produced[hdr] = entry
                    hdr_node = TableArrayHeaderNode()
                    hdr_node.origin = hdr
                    hdr_node.value = hdr
                    static_node = TableArraySectionNode()
                    static_node.header = hdr_node
                    static_node.body = node.body
                    new_nodes.append(static_node)

                lines[idx: idx + 1] = new_nodes
                self._data.update(produced)
                self._data.pop(raw_key, None)

        # ────────────────────────────────── ❷ expand conditional headers
        import re
        for node in list(self._ast.lines):
            # conditional single-bracket section headers
            if isinstance(node, SectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr = node.header.origin

                def _repl(m):
                    var = m.group(1)
                    val = context.get(var, self._data.get(var))
                    return repr(val)

                expr_py = re.sub(r'\$\{([^}]+)\}', _repl, expr)
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

            # conditional table-array section headers
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr = node.header.origin

                def _repl(m):
                    var = m.group(1)
                    val = context.get(var, self._data.get(var))
                    return repr(val)

                expr_py = re.sub(r'\$\{([^}]+)\}', _repl, expr)
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

        # ────────────────────────────────── ❸ collapse & build final mapping
        def _collapse(val: Any, scope: Dict[str, Any]) -> Any:
            from ._ast_nodes import BaseNode

            if isinstance(val, BaseNode):
                val.resolve(self._data, scope, context)
                return _collapse(val.evaluate(), scope)
            if isinstance(val, dict):
                merged = {**scope, **val}
                return {k: _collapse(v, merged) for k, v in val.items()}
            if isinstance(val, list):
                return [_collapse(x, scope) for x in val]
            return val

        final: Dict[str, Any] = {}
        for k, v in list(self._data.items()):
            if k == "__comments__":
                final[k] = v
            else:
                final[k] = _collapse(v, self._data)
                self._data[k] = final[k]

        return final

