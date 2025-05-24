from typing import Any, Dict, List, Optional

import logging
import re
from lark import Tree

from ._make_static import make_static_section
from ._fstring import _evaluate_f_string, _lookup
from ._substitute import _substitute_vars
from ._expression import evaluate_expression_tree
from ._comprehension import iter_environments, _evaluate_comprehension


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # caller can override


class BaseNode:
    def __init__(self):
        self.meta = None  # Parser Metadata
        self.origin = None  # Token or raw source string
        self.value = None  # Semantic value
        self.resolved = None  # Resolved value after substitution
        self.__comments__ = []  # List of comments

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def __repr__(self) -> str:
        if self.meta:
            return f"{self.__class__.__name__}(value={self.value}, start_pos={self.meta.start_pos})"
        else:
            return f"{self.__class__.__name__}(value={self.value})"

    def __eq__(self, other) -> bool:
        """
        Compare AST nodes to strings or other nodes by origin for fidelity in tests.
        """
        # If comparing to a string, check origin equality
        if isinstance(other, str):
            return self.origin == other
        # If comparing to another BaseNode, compare origins
        if isinstance(other, BaseNode):
            return self.origin == other.origin
        return NotImplemented

    def emit(self) -> str:
        raise NotImplementedError(
            f"emit() not implemented for {self.__class__.__name__}"
        )

    def evaluate(self) -> Any:
        return self.resolved if self.resolved is not None else self.value

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        pass

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        return str(self.resolved if self.resolved is not None else self.value)

    def load(self):
        pass


class StartNode(BaseNode):
    def __init__(self, data, contents, origin, meta):
        super().__init__()
        self.lines = []
        self.global_env = {}
        self.data = data
        self.contents = contents
        self.origin = origin
        self.meta = meta

    def emit(self) -> str:
        logger.debug("start.emit() triggered.")
        lines: List[str] = []
        from ._ast_nodes import TableArraySectionNode  # ensure the name is in scope

        for line in self.lines:
            # ── single-bracket sections ───────────────────────────
            if isinstance(line, SectionNode):
                header = line.header.emit()
                lines.append(f"[{header}]")
                for content in line.contents:
                    if isinstance(content, AssignmentNode):
                        lines.append(content.emit())
                    elif isinstance(content, CommentNode):
                        lines.append(content.emit().strip())

            # ── double-bracket (table-array) sections ─────────────
            elif isinstance(line, TableArraySectionNode):
                header = line.header.emit()
                lines.append(f"[[{header}]]")
                for item in getattr(line, "body", []):
                    # only emit assignments and comments; skip untransformed Trees
                    if isinstance(item, AssignmentNode):
                        lines.append(item.emit())
                    elif isinstance(item, CommentNode):
                        lines.append(item.emit().strip())

            # ── top-level assignments ─────────────────────────────
            elif isinstance(line, AssignmentNode):
                lines.append(line.emit())

            # ── standalone comments ───────────────────────────────
            elif isinstance(line, CommentNode):
                lines.append(line.emit().strip())

            # ── blank lines ───────────────────────────────────────
            elif isinstance(line, NewlineNode):
                lines.append("")

            # ── anything else (should be rare) ────────────────────
            else:
                try:
                    emitted = line.emit()
                    if emitted:
                        lines.extend(emitted.split("\n"))
                except Exception:
                    # swallow errors to avoid breaking dumps()
                    pass

        return "\n".join(lines)

    def resolve(
        self, global_env: Optional[Dict] = None, local_env: Optional[Dict] = None
    ):
        env = self.global_env if self.global_env else (global_env or {})
        for line in self.lines:
            line.resolve(env, local_env)
        self.resolved = self.evaluate()

    def evaluate(self) -> Dict:
        result = {}
        for line in self.lines:
            if isinstance(line, SectionNode):
                parts = line.header.value.split(".")
                current_dict = result
                for part in parts[:-1]:
                    current_dict = current_dict.setdefault(part, {})
                current_dict[parts[-1]] = line.evaluate()
        return result

    def render(
        self,
        global_env: Optional[Dict] = None,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        logger.debug("start.render() triggered.")
        return self.emit()


class SectionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.leading_whitespace = None
        self.lbrack = None
        self.header = None
        self.rbrack = None
        self.trailing_whitespace = None
        self.contents = []

    def __str__(self) -> str:
        return f"SectionNode(header={self.header.value if self.header else None})"

    def emit(self) -> str:
        logger.debug("SectionNode.emit() triggered.")
        parts = []
        if self.leading_whitespace:
            parts.append(self.leading_whitespace.value)
        parts.append(self.lbrack.value)
        parts.append(self.header.emit())
        parts.append(self.rbrack.value)
        if self.trailing_whitespace:
            parts.append(self.trailing_whitespace.value)
        if self.__comments__:
            parts.extend(self.__comments__)
        parts.extend(c.emit() for c in self.contents)
        return "\n".join(parts)

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        logger.debug("SectionNode.resolve() triggered.")
        base_env = local_env or {}
        # Pre-populate simple numeric assignments in local scope for header resolution
        for content in self.contents:
            if isinstance(content, AssignmentNode) and isinstance(
                content.value, (IntegerNode, FloatNode)
            ):
                base_env[content.identifier.value] = content.value.evaluate()

        # Resolve header (may generate multiple header_envs in comprehensions)
        self.header.resolve(global_env, base_env)

        self.resolved = {}
        header_env_pairs = getattr(
            self.header, "header_envs", [(self.header.resolved, {})]
        )
        for header_name, alias_env in header_env_pairs:
            scope = {**base_env, **alias_env}
            for line in self.contents:
                line.resolve(global_env, scope)
                if isinstance(line, AssignmentNode):
                    scope[line.identifier.value] = line.resolved
            # Ensure alias bindings persist
            for k, v in alias_env.items():
                scope.setdefault(k, v)
            self.resolved[header_name] = scope

        self.value = self.resolved

    def evaluate(self) -> Dict:
        logger.debug("SectionNode.evaluate() triggered.")
        result = {}
        for content in self.contents:
            if isinstance(content, AssignmentNode):
                result[content.identifier.value] = content.evaluate()
            elif isinstance(content, SectionNode):
                result[content.header.value] = content.evaluate()
        return result

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        logger.debug("SectionNode.render() triggered.")
        # handle comprehension expansion
        if isinstance(self.header, ComprehensionHeaderNode):
            produced = {}
            new_nodes = []
            start_lines = self.meta.parent.lines
            my_idx = start_lines.index(self)
            self.header.render(global_env, local_env or {}, context or {})
            for hdr, alias_env in self.header.header_envs:
                scope = {**alias_env}
                for line in self.contents:
                    line.resolve(global_env, scope, context)
                    if isinstance(line, AssignmentNode):
                        scope[line.identifier.value] = line.evaluate()
                produced[hdr] = scope
                new_nodes.append(make_static_section(hdr, scope))
            start_lines[my_idx : my_idx + 1] = new_nodes
            global_env.update(produced)
            return str(produced)

        simple = {}
        for line in self.contents:
            line.resolve(global_env, simple)
            if isinstance(line, AssignmentNode):
                simple[line.identifier.value] = line.evaluate()
        global_env[self.header.value] = simple
        return str({self.header.value: simple})


class SectionNameNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.parts = []  # List of IDENTIFIER tokens
        self.dots = []  # List of '.' tokens

    def __str__(self) -> str:
        return f"SectionNameNode({self.value})"

    def emit(self) -> str:
        parts = [self.parts[0].value]
        for dot, part in zip(self.dots, self.parts[1:]):
            parts.append(dot.value)
            parts.append(part.value)
        return "".join(parts)

    def evaluate(self) -> str:
        return self.value


class TableArraySectionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.header = None  # TableArrayHeaderNode or ComprehensionHeaderNode
        self.body = []  # List of AssignmentNode, etc.

    def __str__(self) -> str:
        return f"TableArraySectionNode(header={self.header.value if self.header else None})"

    def emit(self) -> str:
        logger.debug("TableArraySectionNode.emit() triggered.")
        parts = [f"[[{self.header.emit()}]]"]
        if self.__comments__:
            parts.extend(self.__comments__)
        parts.extend(item.emit() for item in self.body)
        return "\n".join(parts)

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        logger.debug("TableArraySectionNode.resolve() triggered.")
        local_env = local_env or {}
        for item in self.body:
            if isinstance(item, AssignmentNode) and isinstance(item.value, IntegerNode):
                local_env[item.identifier.value] = item.value.evaluate()
        self.header.resolve(global_env, local_env)
        for item in self.body:
            item.resolve(global_env, local_env)
        self.resolved = self.evaluate()

    def evaluate(self) -> Dict:
        logger.debug("TableArraySectionNode.evaluate() triggered.")
        result = {}
        for line in self.lines:
            if isinstance(line, SectionNode):
                parts = line.header.value.split(".")
                d = result
                for part in parts[:-1]:
                    d = d.setdefault(part, {})
                d[parts[-1]] = line.evaluate()
        return result

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        logger.debug("TableArraySectionNode.render() triggered.")
        parts = [
            f"{item.identifier.value}: {item.render()}"
            for item in self.body
            if isinstance(item, AssignmentNode)
        ]
        return "{" + ", ".join(parts) + "}"


class TableArrayHeaderNode(BaseNode):
    """
    Represents a [[…]] table‑array section header.

    • .origin holds the exact raw header text (including newlines and indentation)
    • .value  holds the clean logical name (used as the mapping key)
    """

    def __init__(self, origin: Optional[str] = None, value: Optional[str] = None):
        super().__init__()
        if origin is not None:
            self.origin = origin
        if value is not None:
            self.value = value

    def emit(self) -> str:
        logger.debug("TableArrayHeaderNode.emit() triggered.")
        # Emit exactly what was parsed—preserving newlines & indent.
        return self.origin

    def evaluate(self) -> str:
        logger.debug("TableArrayHeaderNode.evaluate() triggered.")
        # Returns the logical header name.
        return self.value


class ComprehensionHeaderNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.header_expr = None  # Expression node (e.g., FStringNode)
        self.clauses = None  # ComprehensionClausesNode

    def emit(self) -> str:
        logger.debug("ComprehensionHeaderNode.emit() triggered.")
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        logger.debug("ComprehensionHeaderNode.resolve() triggered.")
        self._evaluate(global_env or {}, local_env or {}, {})

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ):
        logger.debug("ComprehensionHeaderNode.render() triggered.")
        self._evaluate(global_env, local_env or {}, context or {})

    def _evaluate(self, g: Dict, local_env: Dict, ctx: Dict):
        logger.debug("ComprehensionHeaderNode._evaluate() triggered.")
        self.header_envs: List[tuple[str, dict]] = []

        for env in iter_environments(self.clauses, g, local_env, ctx):
            logger.debug(f"ComprehensionHeaderNode._evaluate() env: {env}.")
            scope = {**local_env, **env}
            if ctx is None:
                self.header_expr.resolve(g, scope)
            else:
                self.header_expr.render(g, scope, ctx)

            header_value = (
                self.header_expr.evaluate()
                if hasattr(self.header_expr, "evaluate")
                else self.header_expr
            )
            self.header_envs.append((header_value, env))
        logger.debug(f"ComprehensionHeaderNode.header_envs {self.header_envs}.")

        if not self.header_envs:
            self.resolved = []
        elif len(self.header_envs) > 1:
            self.resolved = [h for h, _ in self.header_envs]
        else:
            self.resolved = self.header_envs[0][0]

        self.value = self.resolved


class AssignmentNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.leading_whitespace = None
        self.trailing_whitespace = None
        self.equals_leading_whitespace = None  # Whitespace before '='
        self.equals_trailing_whitespace = None  # Whitespace after '='
        self.identifier = None
        self.colon = None
        self.type_annotation = None
        self.equals = None
        self.value = None
        self.inline_comment = None

    def emit(self) -> str:
        logger.debug("AssignmentNode.emit() triggered.")
        parts: List[str] = []
        # leading whitespace and identifier
        if self.leading_whitespace:
            parts.append(self.leading_whitespace.value)
        parts.append(self.identifier.value)
        # type annotation if present
        if self.type_annotation:
            parts.append(self.colon.value)
            parts.append(" ")
            parts.append(self.type_annotation.value)
        # equals with surrounding spaces
        parts.append(" ")
        parts.append(self.equals.value if self.equals else "=")
        parts.append(" ")
        # emit the right-hand side value (arrays, nodes, or primitives)
        if hasattr(self.value, "emit"):
            val_text = self.value.emit()
        else:
            val_text = str(self.value)
        # fallback if emit returned None
        if val_text is None:
            val_text = getattr(self.value, "origin", "")
        parts.append(val_text)
        # optional trailing whitespace
        if self.trailing_whitespace:
            parts.append(self.trailing_whitespace.value)
        # inline comment on the assignment
        if self.inline_comment:
            parts.append(self.inline_comment.value)
        return "".join(parts)

    def __str__(self) -> str:
        return f"AssignmentNode({self.identifier.value if self.identifier else None})"

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        """
        Resolve the assignment's right‑hand side, handling both AST nodes,
        folded-expression strings, and manual folded-expression AST values.
        """
        local_env = local_env or {}
        logger.debug("AssignmentNode.resolve() triggered.")
        # ── Handle folded-expression AST nodes (e.g., <(3 + 4)>) ──
        if isinstance(self.value, FoldedExpressionNode):
            # Extract inner arithmetic expression and evaluate safely
            expr = self.value.origin[2:-2].strip()
            from ._eval import safe_eval

            try:
                self.resolved = safe_eval(expr, local_env)
            except Exception:
                # Fallback to original origin if evaluation fails
                self.resolved = self.value.origin
            print(
                f"[DEBUG ASSIGNMENT RESOLVE folded expr AST]: {self.identifier.value} -> {self.resolved}"
            )
            return

        # ── Handle manual folded-expression strings (e.g., '<(3 + 4)>') ──
        if (
            isinstance(self.value, str)
            and self.value.startswith("<(")
            and self.value.endswith(")>")
        ):
            expr = self.value[2:-2].strip()
            from ._eval import safe_eval

            try:
                self.resolved = safe_eval(expr, local_env)
            except Exception:
                self.resolved = self.value
            print(
                f"[DEBUG ASSIGNMENT RESOLVE folded expr]: {self.identifier.value} -> {self.resolved}"
            )
            return

        # ── Delegate to AST node resolution if available ──
        print("[resolve]:", global_env, local_env)
        if hasattr(self.value, "resolve"):
            self.value.resolve(global_env, local_env)
            if hasattr(self.value, "resolved") and self.value.resolved is not None:
                self.resolved = self.value.resolved
            else:
                self.resolved = (
                    self.value.evaluate()
                    if hasattr(self.value, "evaluate")
                    else self.value
                )
        else:
            # Plain Python literal (int, float, bool, None, etc.)
            self.resolved = self.value

        print(f"[DEBUG ASSIGNMENT RESOLVE]: {self.identifier.value} -> {self.resolved}")

    def evaluate(self):
        logger.debug("AssignmentNode.evaluate() triggered.")
        return (
            self.resolved
            if self.resolved is not None
            else (
                self.value.evaluate() if hasattr(self.value, "evaluate") else self.value
            )
        )

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        logger.debug("AssignmentNode.render() triggered.")
        return self.value.render(global_env, local_env or {}, context or {})


class CommentNode(BaseNode):
    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return self.value + "\n"

    def evaluate(self) -> None:
        return None


class NewlineNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.value = "\n"
        self.origin = "\n"

    def emit(self) -> str:
        return self.value

    def evaluate(self) -> None:
        return None


class IntegerNode(BaseNode):
    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return str(self.value)

    def evaluate(self) -> int:
        if self.resolved is not None:
            return self.resolved
        try:
            return int(self.value, 0)  # Auto-detect base for 0o, 0x, 0b
        except ValueError as e:
            print(
                f"[DEBUG INTEGERNODE EVALUATE ERROR]: Invalid integer {self.value}: {e}"
            )
            return self.value

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        try:
            if isinstance(self.value, str):
                self.resolved = int(self.value, 0)  # Auto-detect base for strings
            else:
                self.resolved = int(
                    self.value
                )  # Direct conversion for non-strings (e.g., int)
            self.value = self.resolved
        except ValueError as e:
            print(
                f"[DEBUG INTEGERNODE RESOLVE ERROR]: Invalid integer {self.value}: {e}"
            )
            self.resolved = self.value
        print(f"[DEBUG INTEGERNODE RESOLVE]: {self.value} -> {self.resolved}")


class BooleanNode(BaseNode):
    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return str(self.value).lower()

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        self.resolved = self.value.lower() == "true"
        print(f"[DEBUG BOOLEANNODE RESOLVE]: {self.value} -> {self.resolved}")

    def evaluate(self) -> bool:
        return (
            self.resolved
            if self.resolved is not None
            else (self.value.lower() == "true")
        )


class NullNode(BaseNode):
    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        self.resolved = None
        print(f"[DEBUG NULLNODE RESOLVE]: {self.value} -> {self.resolved}")

    def emit(self) -> str:
        return "null"

    def evaluate(self):
        return None


class FoldedExpressionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.content_tree: Optional[Tree] = None

    def emit(self) -> str:
        logger.debug("FoldedExpressionNode.emit() triggered.")
        # Ensure we always return a string, even if origin was replaced by an int
        return str(self.origin)

    def resolve(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ):
        """
        Phase 2: static folding + placeholder deferral
        - Substitutes @{…} and %{…} immediately.
        - Leaves ${…} intact and wraps the result in an f-string if any remain.
        """

        logger.debug("FoldedExpressionNode.resolve() triggered.")
        # Always pass an empty dict for `context` here so that ${…} tokens
        # get preserved and trigger the f-string branch in evaluate_expression_tree.
        static_ctx: Dict[str, Any] = {}

        # Evaluate without real context, deferring ${…}
        self.resolved = evaluate_expression_tree(
            self.content_tree, global_env, local_env or {}, static_ctx
        )

        # Update origin and value so that subsequent .emit() or lookup
        # returns the folded result (e.g. 'f"...${auth_token}"')
        self.origin = self.resolved
        self.value = self.resolved

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> Any:
        # Phase 3: final inject of context placeholders
        final = evaluate_expression_tree(
            self.content_tree, global_env, local_env or {}, context or {}
        )

        logger.debug("FoldedExpressionNode.render() triggered.")
        return final

    def evaluate(self) -> Any:
        logger.debug("FoldedExpressionNode.evaluate() triggered.")
        # Used by collapse; prefer resolved or fallback to origin
        return self.resolved if self.resolved is not None else self.origin


class InClauseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.keyword = None  # The 'in' keyword

    def __str__(self) -> str:
        return f"InClauseNode(keyword={self.keyword})"

    def emit(self) -> str:
        return self.origin

    def evaluate(self) -> str:
        return self.keyword


class AliasClauseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.keyword = None  # The 'as' keyword
        self.scoped_var = None  # Scoped variable (e.g., '%{x}')

    def __str__(self) -> str:
        return f"AliasClauseNode(keyword={self.keyword}, scoped_var={self.scoped_var})"

    def emit(self) -> str:
        logger.debug("AliasClauseNode.emit() triggered.")

        """
        Emit the alias clause exactly as parsed, preserving the 'as' keyword and the scoped variable.
        """
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        """
        During the static *resolve* phase we only capture the alias *name*.
        The actual value is injected at runtime inside
        _comprehension.iter_environments(), once the anchor item is known.
        """
        logger.debug("AliasClauseNode.resolve() triggered.")
        local_env = local_env or {}

        # ➜ extract the identifier inside %{…}
        raw = getattr(self.scoped_var, "origin", "")
        if raw.startswith("%{") and raw.endswith("}"):
            alias_name = raw[2:-1].split(".")[0]  # drop %{…} and ignore dots
        else:  # (unexpected but safe)
            alias_name = str(self.scoped_var)

        self.resolved = alias_name  # plain string – e.g. "package"
        self.value = alias_name  # let callers read .value directly
        return alias_name

    def evaluate(self) -> Any:
        logger.debug("AliasClauseNode.evaluate() triggered.")
        return self.resolved if self.resolved is not None else self.scoped_var


class PairExprNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.key = None  # Key expression (e.g., (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode), StringExprNode)
        self.value = None  # Value expression

    def __str__(self) -> str:
        return f"PairExprNode(key={self.key}, value={self.value})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        self.key.resolve(global_env, local_env)
        self.value.resolve(global_env, local_env)
        self.resolved = (self.key.resolved, self.value.resolved)
        self.value = self.resolved

    def evaluate(self) -> tuple:
        return (self.key.evaluate(), self.value.evaluate())

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        return f"{self.key.render()}: {self.value.render()}"


class DottedExprNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.dotted_value = None  # Full dotted string, e.g. "package.active"

    def __str__(self) -> str:
        return f"DottedExprNode(dotted_value={self.dotted_value})"

    def emit(self) -> str:
        return self.origin

    def resolve(
        self, global_env: Dict[str, Any], local_env: Optional[Dict[str, Any]] = None
    ):
        local_env = local_env or {}

        # Walk a dotted path through a mapping (dict-like or objects with attrs).
        def _dig(src, path: str):
            cur = src
            for part in path.split("."):
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                elif hasattr(cur, part):
                    cur = getattr(cur, part)
                else:
                    return None
            return cur

        result = _dig(local_env, self.dotted_value)
        if result is None:
            result = _dig(global_env, self.dotted_value)

        self.resolved = result
        # If nothing found, leave the original dotted string as a fallback
        self.value = result if result is not None else self.dotted_value

    def evaluate(self) -> Any:
        return self.resolved if self.resolved is not None else self.dotted_value


class ComprehensionClauseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.loop_vars = []  # List of loop variables
        self.iterable = None  # Iterable expression
        self.conditions = []  # Condition expressions

    def __str__(self) -> str:
        vars_str = " ".join(str(v) for v in self.loop_vars)
        iter_str = str(self.iterable) if self.iterable else ""
        cond_str = " ".join(str(c) for c in self.conditions) if self.conditions else ""
        result = f"for {vars_str} in {iter_str}"
        if cond_str:
            result += f" if {cond_str}"
        return result

    def emit(self) -> str:
        # Emit exactly the stored origin, with no extra whitespace
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        local_env = local_env or {}
        for var in self.loop_vars:
            if isinstance(var, AliasClauseNode):
                var.resolve(global_env, local_env)
                local_env[var.value] = var.resolved
        if hasattr(self.iterable, "resolve"):
            self.iterable.resolve(global_env, local_env)
            iterable_resolved = self.iterable.resolved
        else:
            iterable_resolved = self.iterable
        for cond in self.conditions:
            if hasattr(cond, "resolve"):
                cond.resolve(global_env, local_env)
        self.resolved = {
            "loop_vars": [
                var.resolved
                for var in self.loop_vars
                if isinstance(var, AliasClauseNode)
            ],
            "iterable": iterable_resolved,
            "conditions": [cond.resolved for cond in self.conditions],
        }
        self.value = self.resolved

    def evaluate(self) -> Dict:
        return {
            "loop_vars": [var.evaluate() for var in self.loop_vars],
            "iterable": self.iterable.evaluate(),
            "conditions": [cond.evaluate() for cond in self.conditions],
        }

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        vars_str = ", ".join(var.render() for var in self.loop_vars)
        iter_str = self.iterable.render()
        cond_str = ", ".join(cond.render() for cond in self.conditions)
        result = f"for {vars_str} in {iter_str}"
        if cond_str:
            result += f" if {cond_str}"
        return result


class ComprehensionClausesNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.clauses = []  # List of ComprehensionClauseNode

    def __str__(self) -> str:
        return f"ComprehensionClausesNode(clauses={len(self.clauses)})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        for clause in self.clauses:
            clause.resolve(global_env, local_env)
        self.resolved = [clause.resolved for clause in self.clauses]
        self.value = self.resolved

    def evaluate(self) -> List:
        return [clause.evaluate() for clause in self.clauses]

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        return " ".join(clause.render() for clause in self.clauses)


class StringExprNode(BaseNode):
    """
    Represents a concatenation expression like
        "%{rootDir}" + "/" + "%{name}"
    Resolves each fragment individually and joins them into a single string.
    """

    def __init__(self):
        super().__init__()
        self.parts: list[Any] = []

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        """
        Resolve a concatenation expression into a plain Python value.
        - If there are multiple parts, build a Python f-string that
          interpolates any scoped variables and then evaluate it.
        - If there's exactly one part, just resolve that node directly.
        """
        from ._fstring import _evaluate_f_string
        from ._ast_nodes import (
            LocalScopedVarNode,
            GlobalScopedVarNode,
            SingleQuotedStringNode,
        )

        local_env = local_env or {}

        # Helper to strip quotes from a SingleQuotedStringNode
        def _lit_text(node: SingleQuotedStringNode) -> str:
            return node.origin.strip("\"'")  # drop surrounding quotes

        # -- multiple parts: build and eval an f-string --
        if len(self.parts) > 1:
            segments: list[str] = []
            for part in self.parts:
                if isinstance(part, LocalScopedVarNode) or isinstance(
                    part, GlobalScopedVarNode
                ):
                    # strip the leading marker (%{ or @{) and trailing }
                    inner = part.origin
                    segments.append(f"{inner}")
                elif isinstance(part, SingleQuotedStringNode):
                    segments.append(_lit_text(part))
                else:
                    # resolve any other node to its Python value
                    part.resolve(global_env, local_env)
                    val = part.resolved if hasattr(part, "resolved") else part.value
                    segments.append(str(val))

            # build a quoted Python f-string, e.g. f"{module.name}.py"
            fstring = 'f"' + "".join(segments) + '"'
            # evaluate via our helper
            self.resolved = _evaluate_f_string(
                fstring,
                global_data=global_env,
                local_data=local_env,
                context={},
            )
            self.value = self.resolved
            return

        # -- single part: just resolve that node directly --
        single = self.parts[0]
        single.resolve(global_env, local_env)
        val = getattr(single, "resolved", None)
        if val is None:
            # fallback to its literal or origin if nothing resolved
            val = single.value if hasattr(single, "value") else single.origin
        self.resolved = val
        self.value = self.resolved

    def evaluate(self) -> Any:
        return self.resolved if self.resolved is not None else ""

    def emit(self) -> str:
        # If resolved, emit as a quoted string
        if self.resolved is not None:
            s = str(self.resolved)
            if not (s.startswith('"') or s.startswith("'")):
                s = f'"{s}"'
            return s
        # Before resolution, emit original parts
        return "".join(p.emit() if hasattr(p, "emit") else str(p) for p in self.parts)


class ListComprehensionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.header_expr = None  # Expression for list items
        self.clauses = None  # ComprehensionClausesNode

    def __str__(self) -> str:
        return f"ListComprehensionNode(expr={self.header_expr})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        self.header_expr.resolve(global_env, local_env)
        if self.clauses:
            self.clauses.resolve(global_env, local_env)
        self.resolved = _evaluate_comprehension(self, global_env)
        self.value = self.resolved

    def evaluate(self) -> List:
        return self.resolved if self.resolved is not None else []

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        return f"[{', '.join(str(item) for item in self.evaluate())}]"


class DictComprehensionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.pair = None  # PairExprNode
        self.loop_var = None  # Variable identifier
        self.iterable = None  # Iterable expression
        self.condition = None  # Optional condition expression

    def __str__(self) -> str:
        return f"DictComprehensionNode(pair={self.pair})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        self.pair.resolve(global_env, local_env)
        self.iterable.resolve(global_env, local_env)
        if self.condition:
            self.condition.resolve(global_env, local_env)
        self.resolved = _evaluate_comprehension(self, global_env)
        self.value = self.resolved

    def evaluate(self) -> Dict:
        return self.resolved if self.resolved is not None else {}

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.evaluate().items()) + "}"


class InlineTableComprehensionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.pair = None  # PairExprNode
        self.loop_var = None  # Variable identifier
        self.iterable = None  # Iterable expression
        self.condition = None  # Optional condition expression

    def __str__(self) -> str:
        return f"InlineTableComprehensionNode(pair={self.pair})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        self.pair.resolve(global_env, local_env)
        self.iterable.resolve(global_env, local_env)
        if self.condition:
            self.condition.resolve(global_env, local_env)
        self.resolved = _evaluate_comprehension(self, global_env)
        self.value = self.resolved

    def evaluate(self) -> Dict:
        return self.resolved if self.resolved is not None else {}

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.evaluate().items()) + "}"


class ValueNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.value = None  # Wrapped value (IntegerNode, StringNode, …)
        self.comment = None
        self.inline_comment = (
            None  # Holds Token('INLINE_COMMENT', …) – includes leading spaces
        )
        self.has_comma = (
            False  # True when a ',' token directly followed this item in source
        )

    def emit(self) -> str:
        """Return the exact textual representation for round‑trip serialisation."""
        # ── comment‑only line ───────────────────────────────────────────
        if self.value is None:
            txt = self.inline_comment.value.strip()
            if self.has_comma:
                txt += ","
            return txt

        # ── regular value (may have inline comment) ────────────────────
        base = self.value.emit() if hasattr(self.value, "emit") else str(self.value)
        if self.has_comma:
            base += ","
        if self.inline_comment:
            base += self.inline_comment.value  # already holds leading spaces
        return base

    def __str__(self):
        ic = self.inline_comment.value if self.inline_comment else None
        return f"ValueNode(value={self.value}, inline_comment={ic}, has_comma={self.has_comma})"

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        if hasattr(self.value, "resolve"):
            self.value.resolve(global_env, local_env)
            self.resolved = self.value.resolved
        else:
            self.resolved = self.value

    def evaluate(self):
        return self.value.evaluate() if hasattr(self.value, "evaluate") else self.value

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ):
        return self.value.render() if hasattr(self.value, "render") else str(self.value)


class SLArrayItemNode(ValueNode):
    """
    Represents an item in a single-line array, preserving value, inline comments, and comma.
    """

    def __init__(self):
        super().__init__()
        # Already inherits value, inline_comment, and has_comma from ValueNode


class MLArrayItemNode(ValueNode):
    """
    Represents an item in a multi-line array, preserving value, inline comments, and comma.
    """

    def __init__(self):
        super().__init__()
        # Already inherits value, inline_comment, and has_comma from ValueNode


class InlineTableNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.data = {}

    def emit(self) -> str:
        emit_items = []
        for key, value in self.data.items():
            if isinstance(value, AssignmentNode):
                item = value.emit()
                print(f"[DEBUG INLINE_TABLE EMIT]: {key} -> {item}")
                emit_items.append(item)
            else:
                value_str = value.emit() if hasattr(value, "emit") else str(value)
                emit_items.append(f"{key}={value_str}")
        result = f"{{{', '.join(emit_items)}}}"
        print(f"[DEBUG INLINE_TABLE EMIT RESULT]: {result}")
        return result

    def __str__(self) -> str:
        return f"InlineTableNode(data={len(self.data)})"

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        local_env = local_env or {}
        for key, value in self.data.items():
            # If the value supports resolution, resolve it.
            if hasattr(value, "resolve"):
                value.resolve(global_env, local_env)
                local_env[key] = value.resolved
            else:
                local_env[key] = value
        # Build a dict of resolved values. If the stored item is a node,
        # use its .resolved attribute; otherwise, use the raw value.
        self.resolved = {
            key: value.resolved if hasattr(value, "resolved") else value
            for key, value in self.data.items()
        }
        self.value = self.resolved

    def evaluate(self) -> Dict:
        out = {}
        # Only call .evaluate() if the stored object is a node.
        for key, value in self.data.items():
            if hasattr(value, "evaluate"):
                out[key] = value.evaluate()
            else:
                out[key] = value
        return out

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        # Render each entry; if the entry is a node, call its render method.
        rendered_items = []
        for key, value in self.data.items():
            if hasattr(value, "render"):
                rendered_val = value.render()
            else:
                rendered_val = str(value)
            rendered_items.append(f"{key}: {rendered_val}")
        return "{" + ", ".join(rendered_items) + "}"


class FloatNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.value = None  # The string value, e.g. "inf", "3.14", etc.
        self.origin = None
        self.meta = None
        self.resolved = None  # The actual float, once evaluated/resolved

    def __str__(self) -> str:
        return f"FloatNode(value={self.value})"

    def __repr__(self) -> str:
        return f"FloatNode(value={self.value})"

    def emit(self) -> str:
        # When emitting config text back to a file/string, we just turn the float into a string
        return str(self.value)

    def evaluate(self) -> float:
        """
        Returns the evaluated float value, preferring self.resolved if available.
        If not yet resolved, parse self.value as a float.
        """
        if self.resolved is not None:
            return self.resolved

        # Try calling float() directly. "inf", "-inf", "nan" are valid in Python, but you
        # can add extra checks if you want to handle uppercase, plus-sign, etc.
        self.resolved = float(self.value)
        return self.resolved

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None):
        """
        Forces creation of a float from self.value.
        """
        self.resolved = float(self.value)
        print(f"[DEBUG FLOATNODE RESOLVE]: {self.value} -> {self.resolved}")

    def render(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        """
        Renders the resolved float back to a string (e.g. '3.14' or 'inf').
        """
        return str(self.evaluate())


class SingleQuotedStringNode(BaseNode):
    """
    Represents a single- or double-quoted string, e.g. 'hello' or "world".
    Supports both `${...}` and `%{...}` placeholders.
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return self.origin

    def resolve(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ):
        from ._substitute import _substitute_vars
        from collections.abc import Mapping

        # Initialize environments
        local_env = local_env or {}
        context = context or {}

        # Strip surrounding quotes
        s = self.origin
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            s = s[1:-1]

        # First, substitute `${...}` placeholders using the provided context
        substituted = _substitute_vars(
            s,
            global_env,
            local_env,
            context=context,
            quote_strings=False,
        )

        # Then substitute `%{...}` placeholders via regex
        def repl(match):
            key = match.group(1)
            if key in local_env:
                return str(local_env[key])
            if isinstance(global_env, Mapping) and key in global_env:
                return str(global_env[key])
            return match.group(0)

        result = re.sub(r"%\{([^}]+)\}", repl, substituted)
        self.resolved = result
        self.value = result

    def evaluate(self) -> Any:
        return self.resolved if self.resolved is not None else self.origin


class TripleQuotedStringNode(BaseNode):
    """
    Represents a triple-quoted string, e.g. '''Hello\nWorld''' or \"\"\"Hello\nWorld\"\"\".
    Often multiline.
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        # Re-wrap in triple quotes:
        return f'"""{self.value or ""}"""'

    def resolve(self, global_env, local_env=None):
        # Strip the triple quotes. For example, if origin is """...""", remove them.
        # We assume it's either '''...''' or """..."""
        # This is a naive approach; you could do more robust logic if needed
        # to handle edge cases or multiline strings with embedded quotes.
        stripped = self.origin
        if stripped.startswith('"""') and stripped.endswith('"""'):
            stripped = stripped[3:-3]
        elif stripped.startswith("'''") and stripped.endswith("'''"):
            stripped = stripped[3:-3]

        # Perform variable substitution if your DSL allows that:
        self.resolved = _substitute_vars(
            stripped, global_env, local_env, context={}, quote_strings=False
        )
        self.value = self.resolved

    def evaluate(self):
        return self.resolved if self.resolved else self.origin


class BacktickStringNode(BaseNode):
    """
    Represents a backtick-quoted string, e.g. `some text`.
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return self.origin  # e.g. `abc`

    def resolve(self, global_env, local_env=None):
        # Typically, backticks are used verbatim. But if your DSL allows
        # some variable interpolation or special handling, do it here.
        # Example: Just remove backticks and do a substitution:
        unquoted = self.origin.strip("`")
        self.resolved = _substitute_vars(
            unquoted, global_env, local_env, context={}, quote_strings=False
        )
        self.value = self.resolved

    def evaluate(self):
        return self.resolved if self.resolved is not None else self.origin


class FStringNode(BaseNode):
    """
    Represents an f-string, e.g. f"hello {name}" or f'''hello {name}'''.
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        # Return the original f-string if you want to preserve the 'f' prefix and quotes:
        return self.origin

    def resolve(self, global_env, local_env=None):
        # Use your existing _evaluate_f_string helper to evaluate python-like f-strings
        self.resolved = _evaluate_f_string(
            self.origin, global_data=global_env, local_data=local_env, context={}
        )
        self.value = self.resolved

    def render(self, global_env, local_env=None, context=None):
        self.resolved = _evaluate_f_string(
            self.origin,
            global_data=global_env,
            local_data=local_env,
            context=context or {},
        )
        self.value = self.resolved
        return self.resolved

    def evaluate(self):
        return self.resolved if self.resolved is not None else self.origin


class TripleBacktickStringNode(BaseNode):
    """
    Represents a triple-backtick-quoted string, often used for code blocks.
    Example: ```some code here```
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        """
        Return the original triple-backtick text verbatim, or you
        could re-wrap it with triple backticks if you want uniformity.
        """
        return self.origin

    def resolve(self, global_env, local_env=None):
        """
        If your DSL permits variable interpolation or environment-based substitutions
        inside triple-backtick strings, handle it here. Otherwise, you can treat them
        as literal blocks that remain untouched.
        """
        # Example: Remove the outer ```...```, do your variable substitions, then reassign:
        content = self.origin
        if content.startswith("```") and content.endswith("```"):
            content = content[3:-3]  # remove the leading and trailing ```
        # If you do want to do variable substitution, you might do:
        # content = _substitute_vars(content, global_env, local_env, quote_strings=False)
        self.resolved = content
        self.value = self.resolved

    def evaluate(self):
        """
        Return the resolved content (if any), else fallback to the raw origin.
        """
        return self.resolved if self.resolved is not None else self.origin


class SingleLineArrayNode(BaseNode):
    """
    Represents an array on a single line, e.g. [1, 2, "three"] or ["blue" # Accent color].
    Preserves inline comments for round-trip serialization.
    """

    def __init__(self):
        super().__init__()
        self.lbrack = None  # '[' token
        self.rbrack = None  # ']' token
        self.contents = []  # List of ValueNode
        self.inline_comment = None  # Optional inline comment token
        self.value = []  # Evaluated values (without comments)
        self.resolved = None  # Resolved values after substitution
        self.meta = None  # Parser metadata

    def emit(self) -> str:
        """
        Return a single-line representation, including comments.
        """
        items = [item.emit() for item in self.contents if item]
        content = ", ".join(items) if items else ""
        if self.inline_comment:
            content += f" {self.inline_comment.value}"
        return f"[{content}]"

    def resolve(self, global_env, local_env=None):
        """
        Resolve each item, e.g., substituting variables or evaluating subexpressions.
        Store the fully resolved result in self.resolved.
        """
        resolved_items = []
        for item in self.contents:
            if hasattr(item, "resolve"):
                item.resolve(global_env, local_env)
                resolved_items.append(getattr(item, "resolved", item.value))
            else:
                resolved_items.append(item.value)
        self.resolved = resolved_items
        self.value = resolved_items

    def evaluate(self) -> list:
        """
        Return the evaluated list of items, excluding comments.
        """
        return [
            item.evaluate() if hasattr(item, "evaluate") else item.value
            for item in self.contents
            if item.value is not None
        ]

    def __str__(self) -> str:
        return (
            f"SingleLineArrayNode(value={self.value}, comments={self.inline_comment})"
        )

    def __repr__(self) -> str:
        return f"SingleLineArrayNode(value={self.value})"


class MultiLineArrayNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.lbrack = None  # '[' token
        self.rbrack = None  # ']' token
        self.contents = []  # List of ValueNode
        # We ignore parsed newlines for serialization and instead produce a canonical format.
        self.leading_newlines = None
        self.trailing_newlines = None
        self.value = []
        self.resolved = None
        self.meta = None

    def emit(self) -> str:
        """
        Emit the multiline array in canonical form, preserving both
        values and inline comments exactly as parsed, but omitting
        any blank-only lines.
        """
        lines = ["["]
        for item in self.contents:
            # Get emitted text and strip trailing newline to avoid blank lines
            text = item.emit().rstrip("\n")
            # Skip blank-only lines
            if not text.strip():
                continue
            lines.append(f"  {text}")
        lines.append("]")
        return "\n".join(lines)

    def resolve(self, global_env, local_env=None):
        resolved_items = []
        for item in self.contents:
            if item.value is not None:
                if hasattr(item, "resolve") and callable(item.resolve):
                    item.resolve(global_env, local_env)
                if hasattr(item, "evaluate") and callable(item.evaluate):
                    resolved_items.append(item.evaluate())
                else:
                    resolved_items.append(item.value)
        self.resolved = resolved_items
        self.value = resolved_items

        # Preserve inline comments
        for item in self.contents:
            if item.inline_comment:
                self.__comments__.append(item.inline_comment.value)

    def evaluate(self) -> list:
        return [
            item.evaluate()
            if hasattr(item, "evaluate") and item.value is not None
            else item.value
            for item in self.contents
            if item.value is not None
        ]

    def __str__(self) -> str:
        return f"MultiLineArrayNode(value={self.value}, comments={self.__comments__})"

    def __repr__(self) -> str:
        return f"MultiLineArrayNode(value={self.value})"


class GlobalScopedVarNode(BaseNode):
    """
    Represents a global scoped variable, e.g. @{variable}.
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        # Return the original token text (including "@{...}")
        return self.origin

    def resolve(self, global_env, local_env=None):
        inner = self.origin[2:-1]
        val = _lookup(inner, global_env, {})
        self.resolved = val if val is not None else self.origin
        self.value = self.resolved

    def evaluate(self):
        # Return the inner variable name or fallback to the original token text
        return self.resolved if self.resolved is not None else self.origin


class LocalScopedVarNode(BaseNode):
    """
    Represents a local scoped variable, e.g. %{variable}.
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        # Return the original token text (including "%{...}")
        return self.origin

    def resolve(self, global_env, local_env=None):
        """
        Resolve `%{dotted.path}` against:

        1. the *local_env* created by comprehension aliases,
        2. the whole configuration (`global_env`),

        Supports dotted traversal through **dicts _and_ objects with
        attributes**, so `%{package.name}` works even when `package` is a
        custom class instance.
        """
        from collections.abc import Mapping

        local_env = local_env or {}

        dotted = self.origin[2:-1]  # strip `%{` … `}`

        # ---------------------------------------------------------------- helpers
        def _dig(obj, path: str):
            """Walk *obj* through a dotted path trying both dict keys and attrs."""
            cur = obj
            for part in path.split("."):
                if isinstance(cur, Mapping) and part in cur:
                    cur = cur[part]
                elif hasattr(cur, part):
                    cur = getattr(cur, part)
                else:
                    return None
            return cur

        # ❶ local alias scope
        result = _dig(local_env, dotted)

        # ❷ full configuration
        if result is None:
            result = _dig(global_env, dotted)

        # still unresolved → keep literal to be handled later
        if result is None:
            result = self.origin

        self.resolved = result
        self.value = self.resolved

    def evaluate(self):
        # Return the inner variable name or fallback to the original token text
        return self.resolved if self.resolved is not None else self.origin


class ContextScopedVarNode(BaseNode):
    """
    Represents a context-scoped variable, e.g. ${variable}.
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        # Return the original token text (including "${…}")
        return self.origin

    def resolve(
        self,
        global_env: Dict,
        local_env: Optional[Dict] = None,
    ):
        """
        Replace the ${placeholder} with a concrete value, supporting nested lookups and
        list flattening. Lookup order:
        1. local_env
        2. global_env
        If the lookup yields another AST node (including this one), treat it as missing.
        """
        logger.warning("ContextScopeVariable should not have resolve.")
        from collections.abc import Mapping

        local_env = local_env or {}

        # Extract path segments
        path = self.origin[2:-1]
        parts = path.split(".")

        def _dig(src):
            cur = src
            for part in parts:
                if isinstance(cur, Mapping) and part in cur:
                    cur = cur[part]
                elif hasattr(cur, part):
                    cur = getattr(cur, part)
                elif isinstance(cur, list):
                    out = []
                    for item in cur:
                        val = None
                        if isinstance(item, Mapping) and part in item:
                            val = item[part]
                        elif hasattr(item, part):
                            val = getattr(item, part)
                        if val is None:
                            continue
                        if isinstance(val, list):
                            out.extend(val)
                        else:
                            out.append(val)
                    cur = out
                else:
                    return None
            return cur

        candidate = _dig(global_env)

        # If we got another AST node back, ignore it (to prevent self-reference)
        from ._ast_nodes import BaseNode

        if isinstance(candidate, BaseNode):
            candidate = None

        self.resolved = candidate
        self.value = self.resolved

    def render(
        self,
        global_env: Dict[str, Any],
        local_env: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Any:
        """
        During Config.render we have a *context* dict.  First try to
        resolve the variable against that dict; if not found, fall back
        to the full configuration (global_env + local_env).
        """
        from collections.abc import Mapping

        local_env = local_env or {}
        context = context or {}

        # split e.g. "packages.0.name"
        path = self.origin[2:-1].split(".")

        def _dig(src):
            cur = src
            for part in path:
                if isinstance(cur, Mapping) and part in cur:
                    cur = cur[part]
                elif hasattr(cur, part):
                    cur = getattr(cur, part)
                else:
                    return None
            return cur

        candidate = _dig(context)  # ❶ runtime context
        if candidate is None:
            candidate = _dig(local_env)  # ❷ current local env
        if candidate is None:
            candidate = _dig(global_env)  # ❸ whole config

        self.resolved = candidate
        self.value = candidate
        return candidate


class WhitespaceNode(BaseNode):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def emit(self) -> str:
        return self.value

    def evaluate(self) -> str:
        return self.value


class HspacesNode(BaseNode):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def emit(self) -> str:
        return self.value

    def evaluate(self) -> str:
        return self.value


class InlineWhitespaceNode(BaseNode):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def emit(self) -> str:
        return self.value

    def evaluate(self) -> str:
        return self.value


class ReservedFuncNode(BaseNode):
    """
    Represents a reserved function call like File() or Git().
    """

    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        # Return e.g. "File()" or "Git()"
        return self.origin

    def resolve(self, global_env, local_env=None):
        """
        If your DSL requires special evaluation for `File()` or `Git()`,
        handle it. Otherwise, keep as literal.
        """
        # Example naive: just store it as resolved
        self.resolved = self.origin
        self.value = self.resolved

    def evaluate(self):
        # Return the resolved function call string
        return self.resolved if self.resolved is not None else self.origin
