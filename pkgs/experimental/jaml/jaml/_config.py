from collections.abc import MutableMapping
from copy import deepcopy
from typing import Any, Dict, Optional, Sequence, List, TYPE_CHECKING

from ._fstring import _evaluate_f_string
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # caller can override

if TYPE_CHECKING:
    from ._ast_nodes import BaseNode


class SectionProxy(MutableMapping):
    def __init__(self, config: "Config", prefix: str):
        self._config = config
        self._prefix = prefix

    def _cur_dict(self):
        # grab the nested dict at top‑level key self._prefix
        current = self._config._data
        for part in self._prefix.split("."):
            current = current[part]
        return current

    def __getitem__(self, key: str) -> Any:
        cur = self._cur_dict()
        val = cur[key]
        if isinstance(val, dict):
            # nested SectionProxy for deeper sections
            return SectionProxy(self._config, f"{self._prefix}.{key}")
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        print("SectionProxy setter")
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
        self._rendered_source = None
        print("[DEBUG CONFIG INIT]:", self._data, self._ast)

    def __getitem__(self, key: str) -> Any:
        val = self._data[key]  # only literal keys
        if isinstance(val, dict):
            return SectionProxy(self, key)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        print("Config setter")
        self._data[key] = value  # only literal keys
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
        return any(
            isinstance(k, str) and _normalize(k) == normalized
            for k in self._data
        )

    # ──────────────────────────────────────────────────────── helpers

    def _materialise_comprehension(
        self,
        node,
        concrete_keys: Sequence[str],
        section_map: dict,
    ):
        """
        Replace *node* (whose header is still a ComprehensionHeaderNode) with
        one or more TableArraySectionNode clones so that StartNode.emit() will
        re-serialize the expanded keys exactly.

        • *concrete_keys* – list/tuple of the header strings produced by the
          comprehension, in order.
        • *section_map*   – the body mapping for that section (already popped
          from self._data by the caller).

        Returns nothing.  Mutates self._ast.lines in place.
        """
        from ._ast_nodes import TableArrayHeaderNode

        lines = self._ast.lines
        idx = lines.index(node)

        # convert THIS node to the first key
        first_key = concrete_keys[0]
        node.header = TableArrayHeaderNode(origin=first_key, value=first_key)

        # any additional keys → deep-clone the section node
        for k in concrete_keys[1:]:
            clone = deepcopy(node)
            clone.header = TableArrayHeaderNode(origin=k, value=k)
            idx += 1
            lines.insert(idx, clone)

        # finally, write bodies into _data (caller already handled first one)
        for k in concrete_keys[1:]:
            self._insert_nested_key(k, deepcopy(section_map))

    def _insert_nested_key(self, dotted_key: str, value: Any) -> None:
        """
        Insert *value* into self._data following the dotted path in *dotted_key*
        (e.g. "file.auth.login.source").  Intermediate mappings are created as
        needed.  Any pre-existing scalar encountered on the path is replaced by
        a new mapping.
        """
        cur: Dict[str, Any] = self._data
        parts: List[str] = dotted_key.split(".")
        for part in parts[:-1]:
            if not isinstance(cur.get(part, {}), dict):
                cur[part] = {}
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value
        logger.debug("      ↳ nested-set %s → %r", dotted_key, value)

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
        """Update one assignment while preserving its annotation and section."""
        from lark import Token
        from ._ast_nodes import AssignmentNode, BaseNode, SectionNode
        from ._legacy import _literal

        self._rendered_source = None
        parts = dotted.split(".")
        current = self._ast.data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        key = parts[-1]
        prefix = ".".join(parts[:-1])
        contents = self._ast.lines
        if prefix:
            section = next(
                (
                    node
                    for node in self._ast.lines
                    if isinstance(node, SectionNode)
                    and getattr(node.header, "value", None) == prefix
                ),
                None,
            )
            if section is None:
                raise KeyError(prefix)
            contents = section.contents
        if isinstance(value, BaseNode):
            replacement = value
        elif isinstance(value, str) and value.strip().startswith("<("):
            replacement = self._reparse_value(value)
        elif isinstance(value, str) and value.strip().startswith(
            ('"', "'", 'f"', "f'", "[", "{", "`")
        ):
            replacement = value
        else:
            replacement = self._reparse_value(_literal(value))
        assignment = next(
            (
                node
                for node in contents
                if isinstance(node, AssignmentNode)
                and node.identifier.value == key
            ),
            None,
        )
        if assignment is None:
            assignment = AssignmentNode()
            assignment.identifier = Token("IDENTIFIER", key)
            assignment.equals = Token("SETTER", "=")
            contents.append(assignment)
        assignment.value = replacement
        assignment.resolved = None
        current[key] = replacement

    # round‑trip helpers ------------------------------------------------------
    def dumps(self) -> str:
        """Emit the configuration exactly as it would appear on disk."""
        if self._rendered_source is not None:
            return self._rendered_source
        return self._ast.emit()

    to_jml = dumps

    dump = staticmethod(lambda obj, fp: fp.write(Config.dumps(obj)))  # type: ignore

    # ───────────────────────────────────────────────────────── resolution
    def resolve(self) -> Dict[str, Any]:
        logger.debug("\n\n\n\n⮕ [resolve] entered...")
        from ._eval import safe_eval
        from ._fstring import _eval_fstrings
        from ._comprehension import _eval_comprehensions
        from ._utils import _strip_quotes

        _eval_fstrings(self._data)

        logger.debug("① after _eval_fstrings  → self._data=%r", self._data)

        from ._ast_nodes import (
            BaseNode,
            SectionNode,
            TableArraySectionNode,
            TableArrayHeaderNode,
            ComprehensionHeaderNode,
        )
        import re

        # ② expand conditional headers
        for node in list(self._ast.lines):
            header = getattr(node, "header", None)
            if isinstance(
                node, (SectionNode, TableArraySectionNode)
            ) and isinstance(
                header, (TableArrayHeaderNode, ComprehensionHeaderNode)
            ):  # ← broaden test
                raw_key = header.origin
                expr = raw_key
                logger.debug(
                    "②a processing header raw_key=%s expr=%s", raw_key, expr
                )

                # -- strip alias clauses like "as %{alias}" before placeholder work --
                expr = re.sub(r"\s+as\s+%\{[^}]+\}", "", expr)

                def _scoped_repl(m):
                    var = m.group(1)
                    if var in self._data:
                        v = self._data[var]
                        if isinstance(v, str):
                            v = v.strip(
                                "\"'"
                            )  # ➞ strip any surrounding quotes
                        return repr(v)
                    return "None"

                expr_py = re.sub(r"[@%]\{([^}]+)\}", _scoped_repl, expr)
                expr_py = expr_py.replace("null", "None")
                if "${" in expr_py:
                    logger.debug(
                        "skipping header expression with context placeholders: %s",
                        expr_py,
                    )
                    continue
                logger.debug("executing safe_eval on expr_py=%s", expr_py)
                try:
                    result = safe_eval(expr_py, {})
                except Exception as e:
                    logger.exception(f"exception: {e}")
                    continue

                if not result:
                    self._data.pop(raw_key, None)
                else:
                    section_map = self._data.pop(raw_key, None)
                    if isinstance(result, (list, tuple, set)):
                        import copy

                        for idx, new_key in enumerate(result):
                            tgt_map = (
                                section_map
                                if idx == 0
                                else copy.deepcopy(section_map)
                            )
                            self._insert_nested_key(new_key, tgt_map)
                    else:
                        self._insert_nested_key(result, section_map)
                        node.header.value = result
                        node.header.origin = result

        # ③ collapse all AST nodes into plain Python values
        def _collapse(value: Any, scope: Dict[str, Any]) -> Any:
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
        collapsed = _eval_comprehensions(collapsed)

        # ──────────────────────────────────────────────────────────────
        # ③ post‑process both global‑ and local‑scoped placeholders in strings
        def _expand(val: Any, local_scope: Any) -> Any:
            if isinstance(val, dict):
                return {k: _expand(v, val) for k, v in val.items()}
            if isinstance(val, str):
                pattern = re.compile(r"%\{([^}]+)\}")

                def repl(m):
                    path = m.group(1)
                    tgt = local_scope
                    for part in path.split("."):
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
        return _strip_quotes(final)

    def render(
        self, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Render the parsed JAML AST to a concrete Python object.

        Detailed DEBUG-level logs trace every transformation step so that
        complex scope interactions are visible during troubleshooting.
        """
        logger.debug("\n\n\n\n⮕ [render] entered with context=%r", context)

        # ① expand global- and local-scope f-strings ----------------------
        from ._eval import safe_eval
        from ._fstring import _eval_fstrings
        from ._utils import _strip_quotes
        from ._comprehension import _eval_comprehensions

        _eval_fstrings(self._data)
        logger.debug("① after _eval_fstrings  → self._data=%r", self._data)

        # imports that create circulars if done at module top -------------
        from ._ast_nodes import (
            BaseNode,
            SectionNode,
            TableArraySectionNode,
            TableArrayHeaderNode,
            ComprehensionHeaderNode,
        )
        import re

        # ② expand conditional headers (with context) --------------------
        from ._ast_nodes import (
            ContextScopedVarNode,
            FStringNode,
            SectionNameNode,
        )

        # Bind root context values before header clauses consume them.
        for key, value in list(self._data.items()):
            if isinstance(value, ContextScopedVarNode):
                self._data[key] = value.render(self._data, {}, context or {})

        def render_body(value, scope):
            if isinstance(value, (ContextScopedVarNode, FStringNode)):
                return render_body(
                    value.render(self._data, scope, context), scope
                )
            if isinstance(value, BaseNode):
                value.resolve(self._data, scope)
                return render_body(value.evaluate(), scope)
            if isinstance(value, dict):
                local = {**scope, **value}
                rendered = {}
                for key, item in value.items():
                    rendered[key] = render_body(item, local)
                    local[key] = rendered[key]
                return rendered
            if isinstance(value, list):
                return [render_body(item, scope) for item in value]
            if isinstance(value, str) and value.startswith(('f"', "f'")):
                return _evaluate_f_string(value, self._data, scope, context)
            return value

        for node in list(self._ast.lines):
            header = getattr(node, "header", None)
            if isinstance(header, ComprehensionHeaderNode):
                original_key = header.origin
                header.render(self._data, {}, context or {})
                body = self._data.pop(original_key, {})
                aliases = re.findall(r"\bas\s+%\{([^}]+)\}", original_key)
                clones = []
                for key, environment in header.header_envs:
                    values = render_body(deepcopy(body), environment)
                    for alias in aliases:
                        if alias in environment:
                            values[alias] = environment[alias]
                    self._insert_nested_key(key, values)
                    clone = deepcopy(node)
                    literal = SectionNameNode()
                    literal.value = literal.origin = key
                    clone.header = literal
                    clones.append(clone)
                index = self._ast.lines.index(node)
                self._ast.lines[index : index + 1] = clones
                continue
            if isinstance(
                node, (SectionNode, TableArraySectionNode)
            ) and isinstance(
                header, (TableArrayHeaderNode, ComprehensionHeaderNode)
            ):  # ← broaden test
                raw_key = header.origin
                expr = raw_key
                logger.debug(
                    "②a processing header raw_key=%s expr=%s", raw_key, expr
                )

                # --- ①: Capture alias clause(s) before stripping them for later binding ---
                alias_anchors = re.findall(
                    r"\s+as\s+%\{([^}]+)\}", expr
                )  # get list of aliases (may be empty)
                expr = re.sub(
                    r"\s+as\s+%\{[^}]+\}", "", expr
                )  # strip for python eval
                logger.debug(f"\t- alias_anchors found {alias_anchors}")

                # substitute ${…} placeholders from *context*
                def _context_repl(m):
                    var = m.group(1)
                    v = (context or {}).get(var, None)
                    logger.debug(
                        "   – context placeholder ${%s} -> %r", var, v
                    )
                    if isinstance(v, str):
                        v = v.strip("\"'")
                    return repr(v)

                expr_py = re.sub(r"\$\{([^}]+)\}", _context_repl, expr)

                # substitute @{…} (global) and %{…} (local) placeholders
                def _scoped_repl(m):
                    var = m.group(1)
                    v = self._data.get(var, None)
                    logger.debug("   – scoped placeholder {%s} -> %r", var, v)
                    if isinstance(v, str):
                        v = v.strip("\"'")
                    return repr(v)

                expr_py = re.sub(r"[@%]\{([^}]+)\}", _scoped_repl, expr_py)
                expr_py = expr_py.replace("null", "None")

                logger.debug("   – evaluated Python expr: %s", expr_py)
                try:
                    result = safe_eval(expr_py, {})
                    logger.debug("   – result=%r", result)
                except Exception as exc:
                    logger.exception(
                        "   ✖ header expression failed (%s); leaving untouched",
                        exc,
                    )
                    continue
                if not result:
                    self._data.pop(raw_key, None)
                else:
                    logger.debug(
                        "   – condition truthy → renaming %s → %s",
                        raw_key,
                        result,
                    )
                    section_map = self._data.pop(raw_key, None)
                    if isinstance(result, (list, tuple, set)):
                        # write the first body now – clones handled by helper
                        self._insert_nested_key(result[0], section_map)
                        self._materialise_comprehension(
                            node, list(result), section_map
                        )
                    else:
                        self._insert_nested_key(result, section_map)
                        node.header.value = result
                        node.header.origin = result

                # -- inject alias bindings if present --
                if isinstance(header, ComprehensionHeaderNode):
                    logger.debug("\t- injecting alias bindings")
                    header.render(self._data, {}, context or {})
                    logger.debug(
                        f"\t- processing alias_env {header.header_envs}"
                    )

        logger.debug("② complete  → self._data=%r", self._data)

        # ③ collapse all AST nodes into plain Python values --------------
        def _collapse(value: Any, scope: Dict[str, Any]) -> Any:
            if isinstance(value, (ContextScopedVarNode, FStringNode)):
                return _collapse(
                    value.render(self._data, scope, context), scope
                )
            if isinstance(value, BaseNode):
                value.resolve(self._data, scope)
                return _collapse(value.evaluate(), scope)
            if isinstance(value, dict):
                merged = {**scope, **value}
                return {
                    k: _collapse(v, merged) if k != "__comments__" else v
                    for k, v in value.items()
                }
            if isinstance(value, list):
                return [_collapse(x, scope) for x in value]
            return value

        collapsed = {
            k: v if k == "__comments__" else _collapse(v, self._data)
            for k, v in self._data.items()
        }
        logger.debug("③ collapsed AST         → %r", collapsed)

        # ④ evaluate comprehensions --------------------------------------
        collapsed = _eval_comprehensions(collapsed)
        logger.debug("④ after comprehensions  → %r", collapsed)

        # ⑤ expand remaining f-strings with context ----------------------
        def _eval_context_fstrings(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _eval_context_fstrings(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_eval_context_fstrings(v) for v in obj]
            if isinstance(obj, str) and (
                obj.startswith('f"') or obj.startswith("f'")
            ):
                try:
                    evaluated = _evaluate_f_string(
                        obj,
                        global_data=self._data,
                        local_data={},
                        context=context,
                    )
                    logger.debug("   – f-string %s -> %r", obj, evaluated)
                    return evaluated
                except Exception as exc:
                    logger.debug(
                        "   ✖ f-string %s failed (%s); leaving literal",
                        obj,
                        exc,
                    )
                    return obj
            return obj

        expanded = _eval_context_fstrings(collapsed)
        logger.debug("⑤ after context f-str   → %r", expanded)

        # ⑥ strip surrounding quotes on string literals ------------------
        final = _strip_quotes(expanded)
        # Keep the rendered view serializable without overwriting the deferred
        # expressions needed when the same Config is rendered again.
        from ._legacy import _literal, _lookup

        snapshot = deepcopy(self._ast)
        values = final
        for node in snapshot.lines:
            if isinstance(node, SectionNode):
                try:
                    values = _lookup(node.header.emit(), final)
                except KeyError:
                    continue
                assignments = node.contents
            else:
                assignments = [node]
            for assignment in assignments:
                identifier = getattr(assignment, "identifier", None)
                if identifier is not None and identifier.value in values:
                    assignment.value = _literal(values[identifier.value])
        self._rendered_source = snapshot.emit()
        logger.debug("⭢ [render] returning    → %r", final)
        return final
