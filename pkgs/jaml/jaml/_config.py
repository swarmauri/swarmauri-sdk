from collections.abc import MutableMapping
from typing import Any, Dict, IO, Optional

from ._fstring import _evaluate_f_string


class SectionProxy(MutableMapping):
    def __init__(self, config: "Config", prefix: str):
        self._config = config
        self._prefix = prefix

    def _cur_dict(self):
        # grab the nested dict at top‑level key self._prefix
        return self._config._data[self._prefix]

    def __getitem__(self, key: str) -> Any:
        cur = self._cur_dict()
        val = cur[key]
        if isinstance(val, dict):
            # nested SectionProxy for deeper sections
            return SectionProxy(self._config, f"{self._prefix}.{key}")
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        print('SectionProxy setter')
        cur = self._cur_dict()
        cur[key] = value
        # still sync the AST with the dotted path
        self._config._sync_ast(f"{self._prefix}.{key}", value)

    def __delitem__(self, key: str) -> None:
        cur = self._cur_dict()
        del cur[key]
        self._config._sync_ast(f"{self._prefix}.{key}", None)

    def __iter__(self):
        return iter(self._cur_dict())

    def __len__(self) -> int:
        return len(self._cur_dict())


class Config(MutableMapping):
    """
    A thin wrapper around the parsed AST that preserves round-trip fidelity
    yet behaves like a normal mutable mapping.

    • `resolve()` collapses every AST node and expands **static** f‑strings
      (those that do *not* reference `${…}` context placeholders).

    • `render()` finishes the job, expanding any remaining f‑strings with the
      runtime *context* supplied by the caller.
    """

    # imported lazily to avoid circulars
    from ._ast_nodes import StartNode

    def __init__(self, ast: "Config.StartNode"):
        self._ast = ast
        self._data = ast.data
        print("[DEBUG CONFIG INIT]:", self._data, self._ast)

    def __getitem__(self, key: str) -> Any:
        val = self._data[key]             # only literal keys
        if isinstance(val, dict):
            return SectionProxy(self, key)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        print('Config setter')
        self._data[key] = value           # only literal keys
        self._sync_ast(key, value)

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Config({self._data})"

    def __contains__(self, key: str) -> bool:
        if key in self._data:
            return True
        import re
        def _normalize(s: str) -> str:
            return re.sub(r"\s+", " ", s.strip())
        normalized = _normalize(key)
        return any(isinstance(k, str) and _normalize(k) == normalized for k in self._data)

    # ──────────────────────────────────────────────────────── helpers
    def _reparse_value(self, value: str) -> "BaseNode":
        """
        Parse a value fragment (e.g. folded, array, inline table, comprehension, etc.) by
        wrapping it in a tiny config snippet and using the existing parser + transformer.
        Returns the newly built AST node for that fragment.
        """
        from .api import round_trip_loads
        # Wrap the fragment into a dummy section with a single assignment
        snippet = f"key = {value}\n"
        tmp_cfg = round_trip_loads(snippet)
        # The second line is the AssignmentNode for 'key'
        assign_node = tmp_cfg._ast.lines[0]
        return assign_node.value

    def _sync_ast(self, dotted: str, value: Any):
        print(dotted, value, type(value))
        """
        Sync the underlying AST with mutations to the Config mapping.

        • `dotted` – key in dotted-path form, e.g. "server.port" or "section.key"
        • `value`  – new Python value or AST node assigned by the user
        """
        from ._ast_nodes import (
            AssignmentNode, BaseNode, FoldedExpressionNode, SectionNode,
            SingleQuotedStringNode, IntegerNode, FloatNode, BooleanNode, NullNode
        )

        # Locate the raw data mapping slot
        cur = self._ast.data
        parts = dotted.split('.')
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        key = parts[-1]

        # ──────────────────────────────────────────────────
        # Handle assignments inside sections (e.g., "section.key")
        if len(parts) > 1:
            section_name = parts[0]
            for node in self._ast.lines:
                if isinstance(node, SectionNode) and getattr(node.header, "value", None) == section_name:
                    for content in node.contents:
                        if isinstance(content, AssignmentNode) and content.identifier.value == key:
                            # If the old value was a folded-expression (or the new string looks like one),
                            # reparse it back into a FoldedExpressionNode so resolve() will evaluate it.
                            if (
                                isinstance(content.value, FoldedExpressionNode)
                                or (isinstance(value, str) and value.strip().startswith('<(') and value.strip().endswith(')>'))
                            ):
                                new_node = self._reparse_value(value)
                                content.value    = new_node
                                content.resolved = None
                                cur[key]         = new_node
                            else:
                                # For other raw strings (e.g. list comprehensions), keep as-is
                                content.value    = value
                                content.resolved = None
                                cur[key]         = value
                            return

        # ──────────────────────────────────────────────────
        # Fallback to top-level assignments
        for node in self._ast.lines:
            print(key, node, type(node))
            if not (isinstance(node, AssignmentNode) and node.identifier.value == key):
                print('\n\nbad?')
                continue
            try:
                old = node
                print(old, type(old))

                # wholesale reparse for any AST-backed node updated via a string
                if isinstance(old.value, BaseNode) and isinstance(value, str) and not isinstance(old, SingleQuotedStringNode):
                    print('\n\nhere1')
                    new_node = self._reparse_value(value)
                    node.value    = new_node
                    node.resolved = None
                    cur[key]      = new_node
                    break

                # Direct AST node replacement
                if isinstance(value, BaseNode):
                    print('\n\nhere2')
                    node.value    = value
                    node.resolved = None
                    cur[key]      = value
                    break

                # folded-expression string update (when old was already FoldedExpressionNode)
                if isinstance(value, str) and isinstance(old, FoldedExpressionNode):
                    print('\n\nhere3')
                    new_node = self._reparse_value(value)
                    node.value    = new_node
                    node.resolved = None
                    cur[key]      = new_node
                    break

                # Literal updates: string
                if isinstance(value, str) and isinstance(old, SingleQuotedStringNode):
                    print('\n\nhere4')
                    lit = value if value.startswith(('"', "'")) else f'"{value}"'
                    old.origin    = lit
                    old.value     = value
                    node.resolved = value
                    cur[key]      = value
                    break

                # Literal updates: integer
                if isinstance(value, int) and isinstance(old, IntegerNode):
                    print('\n\nhere5')
                    sval = str(value)
                    old.origin    = sval
                    old.value     = sval
                    old.resolved  = value
                    cur[key]      = value
                    break

                # Literal updates: float
                if isinstance(value, float) and isinstance(old, FloatNode):
                    print('\n\nhere6')
                    sval = str(value)
                    old.origin    = sval
                    old.value     = sval
                    old.resolved  = value
                    cur[key]      = value
                    break

                # Literal updates: boolean
                if isinstance(value, bool) and isinstance(old, BooleanNode):
                    print('\n\nhere bool')
                    bval = "true" if value else "false"
                    old.origin    = bval
                    old.value     = bval
                    old.resolved  = value
                    cur[key]      = value
                    break

                # Literal updates: null
                if value is None and isinstance(old, NullNode):
                    print('\n\n none branch')
                    old.resolved = None
                    cur[key]     = None
                    break

                # Fallback: replace node outright
                print('\n\nfalling back...')
                node.value    = value
                node.resolved = value
                cur[key]      = value
                break

            except Exception as e:
                print(f"_config.Config._sync_ast() failed: '{e}'")





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
                    # Skip context-scoped placeholders (${…}), only expand static f-strings
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
        import re

        # ② expand conditional headers
        for node in list(self._ast.lines):
            # Plain [ … ] sections
            if isinstance(node, SectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr    = node.header.origin

                def _scoped_repl(m):
                    var = m.group(1)
                    if var in self._data:
                        v = self._data[var]
                        if isinstance(v, str):
                            v = v.strip('"\'')      # ➞ strip any surrounding quotes
                        return repr(v)
                    return "None"

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

            # [[ … ]] table-array sections
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr    = node.header.origin

                def _scoped_repl(m):
                    var = m.group(1)
                    if var in self._data:
                        v = self._data[var]
                        if isinstance(v, str):
                            v = v.strip('"\'')
                        return repr(v)
                    return "None"

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

        # ③ collapse all AST nodes into plain Python values
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
            else:
                collapsed[key] = _collapse(val, self._data)

        # ──────────────────────────────────────────────────────────────
        # ◆ evaluate any raw list‑ and dict‑comprehension strings into real Python objects
        list_comp_pattern = re.compile(r'^\s*\[.*\bfor\b.*\]\s*$')
        dict_comp_pattern = re.compile(r'^\s*\{.*\bfor\b.*\}\s*$')

        def _eval_comprehensions(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _eval_comprehensions(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_eval_comprehensions(v) for v in obj]
            if isinstance(obj, str):
                # List comprehensions can be eval’d directly
                if list_comp_pattern.match(obj):
                    try:
                        return eval(obj)
                    except Exception:
                        return obj
                # Dict comprehensions need JAML’s '=' → Python’s ':' conversion
                if dict_comp_pattern.match(obj):
                    # Replace the first '=' before the 'for' with ':' 
                    python_syntax = re.sub(r'=(?=[^}]*\bfor\b)', ':', obj)
                    try:
                        return eval(python_syntax)
                    except Exception:
                        return obj
            return obj

        collapsed = _eval_comprehensions(collapsed)

        # ──────────────────────────────────────────────────────────────
        # ③ post‑process both global‑ and local‑scoped placeholders in strings
        def _expand(val: Any, local_scope: Any) -> Any:
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
                            return "None"
                    return repr(tgt)
                return re.sub(pattern, repl, val)
            return val

        final: Dict[str, Any] = {}
        for k, v in collapsed.items():
            if k == "__comments__":
                final[k] = v
            else:
                final[k] = _expand(v, collapsed)
        return final


    # ──────────────────────────────────────────── render
    def render(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # ────────────────────────────────────────────────────────────────
        # ① expand global- and local-scope f-strings
        def _eval_fstrings(mapping: Dict[str, Any]):
            for key, val in list(mapping.items()):
                if isinstance(val, str) and (val.startswith('f"') or val.startswith("f'")):
                    # Skip context-scoped placeholders (${…}), only expand static f-strings
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
        import re

        # ────────────────────────────────────────────────────────────────
        # ② expand conditional headers (with context)
        for node in list(self._ast.lines):
            if isinstance(node, SectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr    = node.header.origin

                # ②a substitute context placeholders (${…})
                def _context_repl(m):
                    var = m.group(1)
                    if context and var in context:
                        v = context[var]
                        if isinstance(v, str):
                            v = v.strip('"\'')
                        return repr(v)
                    return "None"
                expr_py = re.sub(r'\$\{([^}]+)\}', _context_repl, expr)

                # ②b substitute global (@{…}) and local (%{…}) placeholders
                def _scoped_repl(m):
                    var = m.group(1)
                    if var in self._data:
                        v = self._data[var]
                        if isinstance(v, str):
                            v = v.strip('"\'')
                        return repr(v)
                    return "None"
                expr_py = re.sub(r'[@%]\{([^}]+)\}', _scoped_repl, expr_py)

                expr_py = expr_py.replace('null', 'None')

                try:
                    result = eval(expr_py, {}, {})
                except Exception:
                    continue

                if not result:
                    # remove section when condition is false/None
                    self._data.pop(raw_key, None)
                else:
                    # rename the key to the evaluated result
                    section_map = self._data.pop(raw_key, None)
                    self._data[result] = section_map
                    node.header.value  = result
                    node.header.origin = result

            # handle [[…]] table-array sections similarly
            if isinstance(node, TableArraySectionNode) and isinstance(node.header, TableArrayHeaderNode):
                raw_key = node.header.value
                expr    = node.header.origin

                def _context_repl(m):
                    var = m.group(1)
                    if context and var in context:
                        v = context[var]
                        if isinstance(v, str):
                            v = v.strip('"\'')
                        return repr(v)
                    return "None"
                expr_py = re.sub(r'\$\{([^}]+)\}', _context_repl, expr)

                def _scoped_repl(m):
                    var = m.group(1)
                    if var in self._data:
                        v = self._data[var]
                        if isinstance(v, str):
                            v = v.strip('"\'')
                        return repr(v)
                    return "None"
                expr_py = re.sub(r'[@%]\{([^}]+)\}', _scoped_repl, expr_py)

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

        # ────────────────────────────────────────────────────────────────
        # ③ collapse all AST nodes into plain Python values
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
            else:
                collapsed[key] = _collapse(val, self._data)

        # ────────────────────────────────────────────────────────────────
        # ④ evaluate list- and dict-comprehension strings
        list_comp_pattern = re.compile(r'^\s*\[.*\bfor\b.*\]\s*$')
        dict_comp_pattern = re.compile(r'^\s*\{.*\bfor\b.*\}\s*$')

        def _eval_comprehensions(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _eval_comprehensions(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_eval_comprehensions(v) for v in obj]
            if isinstance(obj, str):
                if list_comp_pattern.match(obj):
                    try:
                        return eval(obj)
                    except Exception:
                        return obj
                if dict_comp_pattern.match(obj):
                    python_syntax = re.sub(r'=(?=[^}]*\bfor\b)', ':', obj)
                    try:
                        return eval(python_syntax)
                    except Exception:
                        return obj
            return obj
        collapsed = _eval_comprehensions(collapsed)

        # ────────────────────────────────────────────────────────────────
        # ⑤ expand any remaining f-strings with the context
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
        expanded = _eval_context_fstrings(collapsed)

        # ────────────────────────────────────────────────────────────────
        # ⑥ strip surrounding quotes from plain strings
        def _strip_quotes(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _strip_quotes(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_strip_quotes(v) for v in obj]
            if isinstance(obj, str) and len(obj) >= 2 and (
                (obj.startswith('"') and obj.endswith('"')) or
                (obj.startswith("'") and obj.endswith("'"))
            ):
                return obj[1:-1]
            return obj
        return _strip_quotes(expanded)
