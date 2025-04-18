from typing import Any, Dict, List, Optional

import ast
import re
from lark import Token, Tree

from ._expression import _render_folded_expression_node, evaluate_expression_tree
from ._fstring import _evaluate_f_string
from ._substitute import _substitute_vars

class BaseNode:
    def __init__(self):
        self.meta = None       # Parser Metadata
        self.origin = None     # Token or raw source string
        self.value = None      # Semantic value
        self.resolved = None   # Resolved value after substitution
        self.__comments__ = [] # List of comments

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def __repr__(self) -> str:
        if self.meta:
            return f"{self.__class__.__name__}(value={self.value}, start_pos={self.meta.start_pos})"
        else:
            return f"{self.__class__.__name__}(value={self.value})"

    def emit(self) -> str:
        raise NotImplementedError(f"emit() not implemented for {self.__class__.__name__}")

    def evaluate(self) -> Any:
        return self.resolved if self.resolved is not None else self.value

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        pass

    def render(self) -> str:
        return str(self.resolved if self.resolved is not None else self.value)

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
        lines = []
        for line in self.lines:
            if isinstance(line, SectionNode):
                header = line.header.emit()
                lines.append(f"[{header}]")
                for content in line.contents:
                    if isinstance(content, AssignmentNode):
                        lines.append(content.emit())
                    elif isinstance(content, CommentNode):
                        lines.append(content.emit().strip())
            elif isinstance(line, CommentNode):
                lines.append(line.emit().strip())
            elif isinstance(line, NewlineNode):
                lines.append("")
        return "\n".join(lines)

    def resolve(self, global_env: Optional[Dict] = None, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        env = self.global_env if self.global_env else (global_env or {})
        for line in self.lines:
            line.resolve(env, local_env, context)
        self.resolved = self.evaluate()

    def evaluate(self) -> Dict:
        result = {}
        for line in self.lines:
            if isinstance(line, SectionNode):
                parts = line.header.value.split('.')
                current_dict = result
                for part in parts[:-1]:
                    current_dict = current_dict.setdefault(part, {})
                current_dict[parts[-1]] = line.evaluate()
        return result

    def render(self) -> str:
        return self.emit()

class SectionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.leading_whitespace = None
        self.lbrack = None            # '[' token
        self.header = None            # SectionNameNode or ComprehensionHeaderNode
        self.rbrack = None            # ']' token
        self.trailing_whitespace = None
        self.contents = []            # List of AssignmentNode, etc.

    def __str__(self) -> str:
        return f"SectionNode(header={self.header.value if self.header else None})"

    def emit(self) -> str:
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

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        local_env = local_env or {}
        for content in self.contents:
            if isinstance(content, AssignmentNode) and isinstance(content.value, (IntegerNode, FloatNode)):
                local_env[content.identifier.value] = content.value.evaluate()
        self.header.resolve(global_env, local_env, context)
        # Handle conditional headers as lists
        headers = self.header.resolved if isinstance(self.header.resolved, list) else [self.header.resolved]
        self.resolved = {}
        for header in headers:
            temp_env = local_env.copy()
            for content in self.contents:
                content.resolve(global_env, temp_env, context)
                if isinstance(content, AssignmentNode):
                    temp_env[content.identifier.value] = content.resolved
            self.resolved[header] = temp_env
        self.value = self.resolved

    def evaluate(self) -> Dict:
        result = {}
        for content in self.contents:
            if isinstance(content, AssignmentNode):
                result[content.identifier.value] = content.evaluate()
            elif isinstance(content, SectionNode):
                result[content.header.value] = content.evaluate()
        return result

    def render(self) -> str:
        parts = [f"{content.identifier.value}: {content.render()}" for content in self.contents
                 if isinstance(content, AssignmentNode)]
        return "{" + ", ".join(parts) + "}"

class SectionNameNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.parts = []  # List of IDENTIFIER tokens
        self.dots = []   # List of '.' tokens

    def __str__(self) -> str:
        return f"SectionNameNode({self.value})"

    def emit(self) -> str:
        parts = [self.parts[0].value]
        for dot, part in zip(self.dots, self.parts[1:]):
            parts.append(dot.value)
            parts.append(part.value)
        return "".join(parts)

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        pass  # Static name, no resolution needed

    def evaluate(self) -> str:
        return self.value

class TableArraySectionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.header = None  # TableArrayHeaderNode or ComprehensionHeaderNode
        self.body = []      # List of AssignmentNode, etc.

    def __str__(self) -> str:
        return f"TableArraySectionNode(header={self.header.value if self.header else None})"

    def emit(self) -> str:
        parts = [f"[[{self.header.emit()}]]"]
        if self.__comments__:
            parts.extend(self.__comments__)
        parts.extend(item.emit() for item in self.body)
        return "\n".join(parts)

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        local_env = local_env or {}
        for item in self.body:
            if isinstance(item, AssignmentNode) and isinstance(item.value, IntegerNode):
                local_env[item.identifier.value] = item.value.evaluate()
        self.header.resolve(global_env, local_env, context)
        for item in self.body:
            item.resolve(global_env, local_env, context)
        self.resolved = self.evaluate()

    def evaluate(self) -> Dict:
        result = {}
        for line in self.lines:
            if isinstance(line, SectionNode):
                parts = line.header.value.split('.')
                d = result
                for part in parts[:-1]:
                    d = d.setdefault(part, {})
                d[parts[-1]] = line.evaluate()
        return result

    def render(self) -> str:
        parts = [f"{item.identifier.value}: {item.render()}" for item in self.body
                 if isinstance(item, AssignmentNode)]
        return "{" + ", ".join(parts) + "}"

class TableArrayHeaderNode(BaseNode):
    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        pass  # Static header, no resolution needed

    def evaluate(self) -> str:
        return self.value

class ComprehensionHeaderNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.header_expr = None  # Expression node (e.g., (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode))
        self.clauses = None      # ComprehensionClausesNode

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.header_expr.resolve(global_env, local_env, context)
        if self.clauses:
            self.clauses.resolve(global_env, local_env, context)
            # Evaluate comprehension to produce header list
            result = []
            for env in evaluate_comprehension_clauses(self.clauses, global_env, local_env, context):
                temp_env = local_env.copy() if local_env else {}
                temp_env.update(env)
                expr_value = self.header_expr.evaluate(global_env, temp_env, context)
                result.append(expr_value)
            self.resolved = result
        else:
            self.resolved = self.header_expr.resolved
        self.value = self.resolved

    def render(self) -> str:
        return self.header_expr.render()

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
        parts = []
        if self.leading_whitespace:
            parts.append(self.leading_whitespace.value)
        parts.append(self.identifier.value)
        if self.type_annotation:
            parts.append(self.colon.value)
            parts.append(self.type_annotation.value)
        parts.append(" ")
        parts.append(self.equals.value if self.equals else "=")
        parts.append(" ")
        if isinstance(self.value, (SingleLineArrayNode, MultiLineArrayNode)):
            # Append the array's emitted text directly without extra indent.
            parts.append(self.value.emit())
        else:
            parts.append(self.value.emit() if hasattr(self.value, "emit") else str(self.value))
        if self.trailing_whitespace:
            parts.append(self.trailing_whitespace.value)
        if self.inline_comment:
            parts.append(self.inline_comment.value)
        return "".join(parts)

    def __str__(self) -> str:
        return f"AssignmentNode({self.identifier.value if self.identifier else None})"

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        print('[resolve]:', global_env, local_env, context)
        if hasattr(self.value, 'resolve'):
            self.value.resolve(global_env, local_env, context)
            self.resolved = self.value.resolved if hasattr(self.value, 'resolved') else self.value.evaluate()
        else:
            if isinstance(self.value, Token):
                if self.value.type == 'INTEGER':
                    try:
                        self.resolved = int(self.value.value, 0)
                    except ValueError:
                        self.resolved = self.value.value
                elif self.value.type == 'FLOAT':
                    try:
                        self.resolved = float(self.value.value)
                    except ValueError:
                        self.resolved = self.value.value
                elif self.value.type == 'SINGLE_QUOTED_STRING':
                    self.resolved = self.value.value.strip('"\'')
                elif self.value.type == 'BOOLEAN':
                    self.resolved = self.value.value == "true"
                elif self.value.type == 'NULL':
                    self.resolved = None
                else:
                    self.resolved = self.value.value
            else:
                self.resolved = self.value
        print(f"[DEBUG ASSIGNMENT RESOLVE]: {self.identifier.value} -> {self.resolved}")

    def evaluate(self):
        return self.resolved if self.resolved is not None else (self.value.evaluate() if hasattr(self.value, 'evaluate') else self.value)

    def render(self) -> str:
        return self.value.render()

class CommentNode(BaseNode):
    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return self.value + "\n"

    def evaluate(self) -> None:
        return None

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        pass  # Comments are static

class NewlineNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.value = '\n'
        self.origin = '\n'

    def emit(self) -> str:
        return self.value

    def evaluate(self) -> None:
        return None

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        pass  # Newlines are static

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
            print(f"[DEBUG INTEGERNODE EVALUATE ERROR]: Invalid integer {self.value}: {e}")
            return self.value

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        try:
            if isinstance(self.value, str):
                self.resolved = int(self.value, 0)  # Auto-detect base for strings
            else:
                self.resolved = int(self.value)  # Direct conversion for non-strings (e.g., int)
            self.value = self.resolved
        except ValueError as e:
            print(f"[DEBUG INTEGERNODE RESOLVE ERROR]: Invalid integer {self.value}: {e}")
            self.resolved = self.value
        print(f"[DEBUG INTEGERNODE RESOLVE]: {self.value} -> {self.resolved}")

class BooleanNode(BaseNode):
    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        return str(self.value).lower()

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.resolved = self.value.lower() == "true"
        print(f"[DEBUG BOOLEANNODE RESOLVE]: {self.value} -> {self.resolved}")

    def evaluate(self) -> bool:
        return self.resolved if self.resolved is not None else (self.value.lower() == "true")

class NullNode(BaseNode):
    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.resolved = None
        print(f"[DEBUG NULLNODE RESOLVE]: {self.value} -> {self.resolved}")

    def emit(self) -> str:
        return "null"

    def evaluate(self):
        return None

class FoldedExpressionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.content_tree = None  # Parse tree for folded content

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.resolved = evaluate_expression_tree(self.content_tree, global_env, local_env, context)
        self.value = self.resolved


class InClauseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.keyword = None  # The 'in' keyword

    def __str__(self) -> str:
        return f"InClauseNode(keyword={self.keyword})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        pass  # Static keyword, no resolution needed

    def evaluate(self) -> str:
        return self.keyword

class AliasClauseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.keyword = None      # The 'as' keyword
        self.scoped_var = None   # Scoped variable (e.g., '%{x}')

    def __str__(self) -> str:
        return f"AliasClauseNode(keyword={self.keyword}, scoped_var={self.scoped_var})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        local_env = local_env or {}
        if isinstance(self.scoped_var, (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode)):
            self.scoped_var.resolve(global_env, local_env, context)
            self.resolved = self.scoped_var.resolved
            local_env[self.value] = self.resolved  # Bind alias
        else:
            self.resolved = self.scoped_var
            local_env[self.value] = self.resolved
        self.value = self.resolved

    def evaluate(self) -> Any:
        return self.resolved if self.resolved is not None else self.scoped_var

class PairExprNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.key = None    # Key expression (e.g., (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode), StringExprNode)
        self.value = None  # Value expression

    def __str__(self) -> str:
        return f"PairExprNode(key={self.key}, value={self.value})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.key.resolve(global_env, local_env, context)
        self.value.resolve(global_env, local_env, context)
        self.resolved = (self.key.resolved, self.value.resolved)
        self.value = self.resolved

    def evaluate(self) -> tuple:
        return (self.key.evaluate(), self.value.evaluate())

    def render(self) -> str:
        return f"{self.key.render()}: {self.value.render()}"

class DottedExprNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.dotted_value = None  # Full dotted string (e.g., "package.active")

    def __str__(self) -> str:
        return f"DottedExprNode(dotted_value={self.dotted_value})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        # Resolve dotted path (e.g., settings.x)
        from ._helpers import resolve_scoped_variable
        self.resolved = resolve_scoped_variable(self.dotted_value, global_env)
        self.value = self.resolved if self.resolved is not None else self.dotted_value

    def evaluate(self) -> Any:
        return self.resolved if self.resolved is not None else self.dotted_value

class ComprehensionClauseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.loop_vars = []    # List of loop variables (e.g., [(SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode), AliasClauseNode])
        self.iterable = None   # Iterable expression (e.g., (SingeLineArrayNode, MultiLineArrayNode), (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode))
        self.conditions = []   # List of condition expressions

    def __str__(self) -> str:
        vars_str = " ".join(str(v) for v in self.loop_vars) if self.loop_vars else ""
        iter_str = str(self.iterable) if self.iterable else ""
        cond_str = " ".join(str(c) for c in self.conditions) if self.conditions else ""
        result = f"for {vars_str} in {iter_str}"
        if cond_str:
            result += f" if {cond_str}"
        return result

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        local_env = local_env or {}
        for var in self.loop_vars:
            if isinstance(var, AliasClauseNode):
                var.resolve(global_env, local_env, context)
                local_env[var.value] = var.resolved
        self.iterable.resolve(global_env, local_env, context)
        for condition in self.conditions:
            condition.resolve(global_env, local_env, context)
        self.resolved = {
            "loop_vars": [var.resolved for var in self.loop_vars if isinstance(var, AliasClauseNode)],
            "iterable": self.iterable.resolved,
            "conditions": [cond.resolved for cond in self.conditions]
        }
        self.value = self.resolved

    def evaluate(self) -> Dict:
        return {
            "loop_vars": [var.evaluate() for var in self.loop_vars],
            "iterable": self.iterable.evaluate(),
            "conditions": [cond.evaluate() for cond in self.conditions]
        }

    def render(self) -> str:
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

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        for clause in self.clauses:
            clause.resolve(global_env, local_env, context)
        self.resolved = [clause.resolved for clause in self.clauses]
        self.value = self.resolved

    def evaluate(self) -> List:
        return [clause.evaluate() for clause in self.clauses]

    def render(self) -> str:
        return " ".join(clause.render() for clause in self.clauses)

class StringExprNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.parts = []  # List of (SingleQuotedStringNode, TripleQuotedStringNode, BacktickStringNode, FStringNode, TripleBacktickStringNode) or StringExprNode

    def __str__(self) -> str:
        return f"StringExprNode(parts={len(self.parts)})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        resolved_parts = []
        for part in self.parts:
            part.resolve(global_env, local_env, context)
            resolved_parts.append(part.resolved)
        self.resolved = "".join(str(part) for part in resolved_parts)
        self.value = self.resolved

    def evaluate(self) -> str:
        return self.resolved if self.resolved is not None else "".join(str(part.value) for part in self.parts)

class ListComprehensionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.header_expr = None  # Expression for list items
        self.clauses = None      # ComprehensionClausesNode

    def __str__(self) -> str:
        return f"ListComprehensionNode(expr={self.header_expr})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.header_expr.resolve(global_env, local_env, context)
        if self.clauses:
            self.clauses.resolve(global_env, local_env, context)
        self.resolved = evaluate_comprehension(self, global_env)
        self.value = self.resolved

    def evaluate(self) -> List:
        return self.resolved if self.resolved is not None else []

    def render(self) -> str:
        return f"[{', '.join(str(item) for item in self.evaluate())}]"

class DictComprehensionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.pair = None       # PairExprNode
        self.loop_var = None   # Variable identifier
        self.iterable = None   # Iterable expression
        self.condition = None  # Optional condition expression

    def __str__(self) -> str:
        return f"DictComprehensionNode(pair={self.pair})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.pair.resolve(global_env, local_env, context)
        self.iterable.resolve(global_env, local_env, context)
        if self.condition:
            self.condition.resolve(global_env, local_env, context)
        self.resolved = evaluate_comprehension(self, global_env)
        self.value = self.resolved

    def evaluate(self) -> Dict:
        return self.resolved if self.resolved is not None else {}

    def render(self) -> str:
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.evaluate().items()) + "}"

class InlineTableComprehensionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.pair = None       # PairExprNode
        self.loop_var = None   # Variable identifier
        self.iterable = None   # Iterable expression
        self.condition = None  # Optional condition expression

    def __str__(self) -> str:
        return f"InlineTableComprehensionNode(pair={self.pair})"

    def emit(self) -> str:
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        self.pair.resolve(global_env, local_env, context)
        self.iterable.resolve(global_env, local_env, context)
        if self.condition:
            self.condition.resolve(global_env, local_env, context)
        self.resolved = evaluate_comprehension(self, global_env)
        self.value = self.resolved

    def evaluate(self) -> Dict:
        return self.resolved if self.resolved is not None else {}

    def render(self) -> str:
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.evaluate().items()) + "}"

class ValueNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.value = None  # Wrapped value (e.g., IntegerNode, SingleQuotedStringNode, etc.)
        self.comment = None
        self.inline_comment = None  # New attribute to hold an inline comment

    def emit(self) -> str:
        # Emit the base value, then append the inline comment (if present)
        base = self.value.emit() if hasattr(self.value, "emit") else str(self.value)
        if self.inline_comment:
            base += " " + self.inline_comment.value
        return base

    def __str__(self) -> str:
        # Include inline_comment information for debugging output
        ic = self.inline_comment.value if self.inline_comment else None
        return f"ValueNode(value={self.value}, inline_comment={ic})"

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        if hasattr(self.value, "resolve"):
            self.value.resolve(global_env, local_env, context)
            self.resolved = self.value.resolved
        else:
            self.resolved = self.value

    def evaluate(self) -> Any:
        # Evaluate using the wrapped value’s evaluate() method if available
        return self.value.evaluate() if hasattr(self.value, "evaluate") else self.value

    def render(self) -> str:
        # Delegate the rendering to the wrapped value (or convert to string)
        return self.value.render() if hasattr(self.value, "render") else str(self.value)


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

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        local_env = local_env or {}
        for key, value in self.data.items():
            # If the value supports resolution, resolve it.
            if hasattr(value, "resolve"):
                value.resolve(global_env, local_env, context)
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

    def render(self) -> str:
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
        self.value = None      # The string value, e.g. "inf", "3.14", etc.
        self.origin = None
        self.meta = None
        self.resolved = None   # The actual float, once evaluated/resolved

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

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        """
        Forces creation of a float from self.value.
        """
        self.resolved = float(self.value)
        print(f"[DEBUG FLOATNODE RESOLVE]: {self.value} -> {self.resolved}")

    def render(self) -> str:
        """
        Renders the resolved float back to a string (e.g. '3.14' or 'inf').
        """
        return str(self.evaluate())



class SingleQuotedStringNode(BaseNode):
    """
    Represents a single- or double-quoted string, e.g. 'hello' or "world".
    """
    def __init__(self):
        super().__init__()

    def emit(self) -> str:
        # Return the original text (including the single/double quotes),
        # or re-quote if you want to unify them.
        return self.origin

    def resolve(self, global_env, local_env=None, context=None):
        # Remove the leading and trailing ' or "
        unquoted = self.origin.strip('"\'')
        # If you support variable interpolation, substitute them:
        self.resolved = _substitute_vars(unquoted, global_env, local_env, context=context, quote_strings=False)
        self.value = self.resolved

    def evaluate(self):
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

    def resolve(self, global_env, local_env=None, context=None):
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
        self.resolved = _substitute_vars(stripped, global_env, local_env, context=context, quote_strings=False)
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

    def resolve(self, global_env, local_env=None, context=None):
        # Typically, backticks are used verbatim. But if your DSL allows
        # some variable interpolation or special handling, do it here.
        # Example: Just remove backticks and do a substitution:
        unquoted = self.origin.strip('`')
        self.resolved = _substitute_vars(unquoted, global_env, local_env, context=context, quote_strings=False)
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

    def resolve(self, global_env, local_env=None, context=None):
        # Use your existing _evaluate_f_string helper to evaluate python-like f-strings
        self.resolved = _evaluate_f_string(
            self.origin,
            global_data=global_env,
            local_data=local_env,
            context=context
        )
        self.value = self.resolved

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

    def resolve(self, global_env, local_env=None, context=None):
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
        # content = _substitute_vars(content, global_env, local_env, context, quote_strings=False)
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
        self.lbrack = None              # '[' token
        self.rbrack = None              # ']' token
        self.contents = []              # List of ValueNode
        self.inline_comment = None      # Optional inline comment token
        self.value = []                 # Evaluated values (without comments)
        self.resolved = None            # Resolved values after substitution
        self.meta = None                # Parser metadata

    def emit(self) -> str:
        """
        Return a single-line representation, including comments.
        """
        items = [item.emit() for item in self.contents if item]
        content = ", ".join(items) if items else ""
        if self.inline_comment:
            content += f" {self.inline_comment.value}"
        return f"[{content}]"

    def resolve(self, global_env, local_env=None, context=None):
        """
        Resolve each item, e.g., substituting variables or evaluating subexpressions.
        Store the fully resolved result in self.resolved.
        """
        resolved_items = []
        for item in self.contents:
            if hasattr(item, "resolve"):
                item.resolve(global_env, local_env, context)
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
        return f"SingleLineArrayNode(value={self.value}, comments={self.inline_comment})"

    def __repr__(self) -> str:
        return f"SingleLineArrayNode(value={self.value})"


class MultiLineArrayNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.lbrack = None              # '[' token
        self.rbrack = None              # ']' token
        self.contents = []              # List of ValueNode
        # We ignore parsed newlines for serialization and instead produce a canonical format.
        self.leading_newlines = None    
        self.trailing_newlines = None   
        self.__comments__ = []          # List of comments
        self.value = []                 # Evaluated values
        self.resolved = None            
        self.meta = None                

    def emit(self) -> str:
        """
        Emit the multiline array in a canonical format:
        
        [
          item1, <optional inline comment>
          item2, <optional inline comment>
          item3   <optional inline comment>
        ]
        
        with exactly one newline after '[' and before ']', and exactly two spaces of indent.
        A trailing comma is added for all items except the last.
        """
        indent = "  "  # exactly two spaces per item
        newline = "\n"
        lines = []
        for idx, item in enumerate(self.contents):
            if item.value is not None:
                item_str = item.value.emit() if hasattr(item.value, "emit") else str(item.value)
                # Add a comma if there is a subsequent non-comment value.
                need_comma = any(
                    self.contents[j].value is not None
                    for j in range(idx + 1, len(self.contents))
                )
                if need_comma:
                    item_str += ","
                if item.inline_comment:
                    item_str += " " + item.inline_comment.value
                lines.append(indent + item_str)
            elif item.inline_comment:
                lines.append(indent + item.inline_comment.value)
        content = newline.join(lines)
        return f"[{newline}{content}{newline}]"

    def resolve(self, global_env, local_env=None, context=None):
        resolved_items = []
        for item in self.contents:
            # Only process nodes that have a meaningful value.
            if item.value is not None:
                if hasattr(item, "resolve") and callable(item.resolve):
                    item.resolve(global_env, local_env, context)
                if hasattr(item, "evaluate") and callable(item.evaluate):
                    resolved_item = item.evaluate()
                else:
                    resolved_item = item.value
                resolved_items.append(resolved_item)
        self.resolved = resolved_items
        self.value = resolved_items

        # Optionally, preserve inline comments separately.
        for item in self.contents:
            if item.inline_comment:
                self.__comments__.append(item.inline_comment.value)

    def evaluate(self) -> list:
        return [
            item.evaluate() if hasattr(item, "evaluate") and item.value is not None else item.value
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

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        # Expecting self.origin to be a string like "@{variable}"
        if self.origin.startswith("@{") and self.origin.endswith("}"):
            self.resolved = self.origin[2:-1]
        else:
            self.resolved = self.origin
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

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        # Expecting self.origin to be a string like "%{variable}"
        if self.origin.startswith("%{") and self.origin.endswith("}"):
            self.resolved = self.origin[2:-1]
        else:
            self.resolved = self.origin
        self.value = self.resolved

    def evaluate(self):
        # Return the inner variable name or fallback to the original token text
        return self.resolved if self.resolved is not None else self.origin


class ContextScopedVarNode(BaseNode):
    """
    Represents a context scoped variable, e.g. ${variable}.
    """
    def __init__(self):
        super().__init__()
    
    def emit(self) -> str:
        # Return the original token text (including "${...}")
        return self.origin

    def resolve(self, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None):
        # Expecting self.origin to be a string like "${variable}"
        if self.origin.startswith("${") and self.origin.endswith("}"):
            self.resolved = self.origin[2:-1]
        else:
            self.resolved = self.origin
        self.value = self.resolved

    def evaluate(self):
        # Return the inner variable name or fallback to the original token text
        return self.resolved if self.resolved is not None else self.origin


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

    def resolve(self, global_env, local_env=None, context=None):
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

