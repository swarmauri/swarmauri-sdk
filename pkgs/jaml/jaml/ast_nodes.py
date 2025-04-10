import re
from ._helpers import (
    unquote, 
    resolve_scoped_variable, 
    evaluate_f_string, 
    evaluate_f_string_interpolation,
    evaluate_comprehension
)  

class InClause:
    """
    Represents an 'in' clause keyword in a comprehension.
    
    Attributes:
      keyword: The literal keyword (expected to be "in").
      original: The original raw text for this token, for round-trip fidelity.
    """
    def __init__(self, keyword, original):
        self.keyword = keyword
        self.origin = original

    def __str__(self):
        # Return the original text to preserve formatting.
        return self.origin

    def __repr__(self):
        return f"InClause(keyword={self.keyword!r}, origin={self.origin!r})"


class AliasClause:
    """
    Represents the alias keyword in a comprehension clause.
    
    This node is created from an "AS" occurrence and is intended to be used
    in comprehension clauses where an alias is specified (e.g. "for x as %{x}")
    
    Attributes:
      keyword: The literal keyword value (expected to be "as").
      original: The original raw text for this keyword (for round-trip fidelity).
    """
    def __init__(self, keyword, original):
        self.keyword = keyword
        self.origin = original

    def __str__(self):
        # For resolution or unparse, returning the original text is useful.
        return self.origin

    def __repr__(self):
        return f"AliasClause(keyword={self.keyword!r}, original={self.origin!r})"


class PairExpr:
    """
    Represents a key-value pair expression (e.g. "k = v" or "k : v").
    
    Attributes:
      key: The left-hand side of the expression (a string_expr, IDENTIFIER, or computed node).
      value: The right-hand side expression.
      original: The exact original text for this pair expression for round-trip purposes.
    """
    def __init__(self, key, value, original):
        self.key = key
        self.value = value
        self.origin = original

    def __str__(self):
        # For evaluation or debugging, it could output in a key = value form.
        return f"{self.key} = {self.value}"

    def __repr__(self):
        return f"PairExpr(key={self.key!r}, value={self.value!r}, origin={self.origin!r})"


class DottedExpr:
    """
    Represents a dotted expression, e.g. "package.active".
    
    Attributes:
      dotted_value: The full computed string (e.g., "package.active").
      original: The original raw text as captured from the input.
    """
    def __init__(self, dotted_value, original):
        self.dotted_value = dotted_value
        self.origin = original

    def __str__(self):
        # Returning the computed dotted value can be useful for evaluation.
        return self.dotted_value

    def __repr__(self):
        return f"DottedExpr(dotted_value={self.dotted_value!r}, origin={self.origin!r})"


class ComprehensionClause:
    """
    Represents a single comprehension clause extracted from a comprehension expression.
    
    For example, in a comprehension such as:
    
       for package as %{package} in @{packages} if package.active
    
    It stores:
      - loop_vars: the list of loop variable expressions (which might include constructs like
                   'package' or 'package as %{package}').
      - iterable: the expression yielding an iterable (e.g. '@{packages}').
      - conditions: any condition parts (e.g. 'package.active').
      - original: the original text slice for this clause (for round-trip and debugging).
    """
    def __init__(self, loop_vars, iterable, conditions, original):
        self.loop_vars = loop_vars
        self.iterable = iterable
        self.conditions = conditions
        self.origin = original

    def __str__(self):
        # Produce a readable string representation.
        vars_str = " ".join(str(v) for v in self.loop_vars) if self.loop_vars else ""
        iter_str = str(self.iterable) if self.iterable else ""
        cond_str = " ".join(str(c) for c in self.conditions) if self.conditions else ""
        result = f"for {vars_str} in {iter_str}"
        if cond_str:
            result += " if " + cond_str
        return result

    def __repr__(self):
        return (f"ComprehensionClause(loop_vars={self.loop_vars!r}, "
                f"iterable={self.iterable!r}, conditions={self.conditions!r}, "
                f"origin={self.origin!r})")


class ComprehensionClauses:
    """
    Represents a group of comprehension_clause nodes produced by the comprehension_clauses rule.
    
    Attributes:
      clauses: A list of comprehension_clause AST nodes.
      original: The raw original text for the comprehension clauses (as captured by meta).
    """
    def __init__(self, clauses, original):
        self.clauses = clauses
        self.origin = original

    def __str__(self):
        # Optionally, join the string representations of each clause.
        return " ".join(str(clause) for clause in self.clauses)

    def __repr__(self):
        return f"ComprehensionClauses(clauses={self.clauses!r}, origin={self.origin!r})"


class StringExpr:
    """
    Represents a concatenated string expression composed of one or more components
    (which may be literals (PreservedString) or scoped variables).
    
    Attributes:
      parts: A list of components (results from STRING, SCOPED_VAR, etc.) that are to be concatenated.
      original: The raw text of the string expression, as extracted from the source (for round-trip purposes).
    """
    def __init__(self, parts, original):
        self.parts = parts
        self.origin = original

    def __str__(self):
        # For debugging or resolution purposes, we may choose to join the parts.
        # Here we join their string representation.
        return "".join(str(part) for part in self.parts)

    def __repr__(self):
        return f"StringExpr(parts={self.parts!r}, origin={self.origin!r})"


class TableArraySectionNode:
    """
    Represents a table array section as defined by double brackets [[ ... ]].
    
    Attributes:
      header: The header expression (which may be computed by a comprehension)
              that determines the key for the table array.
      body: A list of child nodes corresponding to the table array content.
      original: The exact original text (slice from the input) that produced this section.
    """
    def __init__(self, header, body, original):
        self.header = header
        self.body = body  # Typically a list of assignment nodes and/or nested sections.
        self.origin = original

    def __str__(self):
        # For round-trip, if no modifications have been made, you could return the original.
        # Otherwise, you could reconstruct it. Here, we reconstruct it with double brackets.
        header_str = str(self.header)  # assume header unparse produces a computed header string.
        # Reconstruct the body by joining each unparsed line (this assumes your unparse_node handles each child).
        body_str = "\n".join(str(item) for item in self.body)
        return f"[[{header_str}]]\n{body_str}"

    def __repr__(self):
        return (f"TableArraySectionNode(header={self.header!r}, "
                f"body={self.body!r}, origin={self.origin!r})")


class TableArrayComprehensionHeader:
    """
    Represents a computed header for a table array section.
    
    This node is produced from the `table_array_comprehension` rule
    and is distinct from the DeferredListComprehension because it supports
    the "as" syntax or other extra constructs that may be present.
    
    Attributes:
      header_expr: The initial comprehension expression (e.g. a string_expr or computed value).
      clauses: The comprehension clauses (may include "for ... as ..." parts)
      original: The full original text for the header (preserved for round-trip).
    """
    def __init__(self, header_expr, clauses, original):
        self.header_expr = header_expr
        self.clauses = clauses
        self.origin = original

    def __str__(self):
        # For debugging, you might return the original text.
        return self.origin

    def __repr__(self):
        return (f"TableArrayComprehensionHeader(header_expr={self.header_expr!r}, "
                f"clauses={self.clauses!r}, origin={self.origin!r})")


class TableArrayHeader:
    """
    Represents the header for a table array section.
    
    Attributes:
      header_expr: The computed header expression (e.g. a section name, a STRING,
                   or a comprehension node) parsed from the table_array_header.
      original: The original text for the header, as sliced from the source input.
    """
    def __init__(self, header_expr, original):
        self.header_expr = header_expr
        self._origin = original

    def __str__(self):
        # When converting to string, return the original text
        return self._origin

    def __repr__(self):
        return f"TableArrayHeader(header_expr={self.header_expr!r}, origin={self._origin!r})"


class FoldedExpressionNode:
    """
    Represents a folded (immediate) expression from the config,
    preserving the original bracketed text for round-trip and optional later
    evaluation in the resolve step.
    """

    def __init__(self, original_text: str, content_tree):
        # Store original in a private variable.
        self._original = original_text
        self.content_tree = content_tree  # This is the parse subtree from folded_content

    @property
    def origin(self) -> str:
        """Getter for the original text."""
        return self._original

    @origin.setter
    def origin(self, new_text):
        """
        Setter for the original text.
        Whenever the original text is updated, re-parse it to update the content_tree.
        Only update if new_text is a string.
        """
        if not isinstance(new_text, str):
            # If it's not a string (for example, an arithmetic result), leave self._original unchanged.
            return
        self._original = new_text
        self.content_tree = self._parse_original(new_text)

    def _parse_original(self, text: str):
        """
        Parses the given folded expression text into a content tree.
        Strips off the '<(' and ')>' delimiters before invoking the parser.
        """
        try:
            from .lark_parser import parser
            return parser.parse(text)
        except Exception as e:
            raise ValueError(f"Unable to parse and transform folded expression: {text} due to '{e}'") from e

    def __str__(self):
        """
        When converting to a string (e.g. for debug prints),
        return the bracketed text exactly as read from the file.
        """
        return self._original

    def __repr__(self):
        return f"FoldedExpressionNode(origin={self._original!r}, content_tree={self.content_tree!r})"

    def __eq__(self, other):
        if isinstance(other, str):
            return self._original == other
        if isinstance(other, FoldedExpressionNode):
            return self._original == other._original
        return False

    def get_inner_expression(self) -> str:
        """
        Parses out the inner expression for resolution by stripping off the
        leading '<(' and trailing ')>'.
        """
        stripped = self._original.strip()
        if stripped.startswith("<(") and stripped.endswith(")>"):
            return stripped[2:-2].strip()
        return stripped


class DeferredListComprehension:
    """
    Represents a deferred list comprehension.
    It preserves the original raw text (including square brackets)
    so that after round-trip loads, the original text is maintained.
    Its evaluate(env) method computes the list given an environment.
    """
    def __init__(self, text):
        # text should be the entire raw text including the square brackets,
        # e.g., '[f"item_{x}" for x in [1, 2, 3]]'
        self.text = text

    @property
    def origin(self):
        return self.text

    @origin.setter
    def origin(self, value):
        self.text = value

    @property
    def value(self):
        return self.text

    def evaluate(self, env):
        """
        Evaluate the deferred list comprehension.
        Expected syntax: [f"item_{x}" for x in [1, 2, 3]]
        The method uses a regex to capture the f-string expression, loop variable, and iterable expression.
        It then evaluates the f-string expression for each element of the iterable.
        """
        pattern = r'^\[\s*(f["\'].*?["\'])\s+for\s+(\w+)\s+in\s+(.*)\s*\]$'
        m = re.match(pattern, self.text.strip())
        if not m:
            return self.text
        expr_str, loop_var, iterable_str = m.groups()
        try:
            iterable = eval(iterable_str, {"__builtins__": {}}, env)
        except Exception:
            return self.text
        result = []
        for item in iterable:
            local_env = {loop_var: item}
            # Evaluate the f-string expression via the interpolation helper.
            value = evaluate_f_string_interpolation(expr_str, local_env)
            result.append(value)
        return result

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"DeferredListComprehension({self.text!r})"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.text == other
        if isinstance(other, DeferredListComprehension):
            return self.text == other.text
        return False




class DeferredDictComprehension:
    def __init__(self, text):
        self.origin_text = text  # The raw inner text, or full text including braces

    @property
    def origin(self):
        return self.origin_text

    @origin.setter
    def origin(self, value):
        self.origin_text = value

    def evaluate(self, env):
        # (Your existing implementation that uses self.origin_text.)
        pattern = r'^(f["\'].*?["\'])\s*(?::|=)\s*(.*?)\s+for\s+(\w+)\s+in\s+(.*)$'
        m = re.match(pattern, self.origin_text.strip().strip('{}'))
        if not m:
            return self.origin_text
        key_expr_str, val_expr_str, loop_var, iterable_str = m.groups()
        try:
            iterable = eval(iterable_str, {"__builtins__": {}}, env)
        except Exception:
            return self.origin_text
        result = {}
        for item in iterable:
            local_env = {loop_var: item}
            key = evaluate_f_string_interpolation(key_expr_str, local_env)
            try:
                value = eval(val_expr_str, {"__builtins__": {}}, local_env)
            except Exception:
                value = val_expr_str
            result[key] = value
        return result
    def __str__(self):
        return "{" + self.origin_text + "}"
    def __repr__(self):
        return f"DeferredDictComprehension({self.origin_text!r})"
    def __eq__(self, other):
        if isinstance(other, str):
            return self.origin_text == other
        if isinstance(other, DeferredDictComprehension):
            return self.origin_text == other.origin_text
        return False


class PreservedString(str):
    def __new__(cls, value, original):
        # Create a new string instance using the unquoted value.
        obj = super().__new__(cls, value)
        obj.value = value
        obj._origin = original  # store the original text, e.g. '"Hello, World!"'
        return obj

    @property
    def origin(self):
        return f"{self._origin}"

    @origin.setter
    def origin(self, value):
        self.value = value
        self._origin = value
 
    def __str__(self):
        # When converting to string for round-trip output, return the original quoted text.
        return self._origin

    def __repr__(self):
        return f"PreservedString(value={super().__str__()!r}, origin={self._origin!r})"

    def __reduce_ex__(self, protocol):
        """
        Tells pickle/deepcopy how to re-create a PreservedString instance.
        Returns (constructor, args) so that __new__ is called correctly.
        """
        return (
            self.__class__,
            (self.value, self._origin)  # The args we pass to __new__
        )

class PreservedValue:
    def __init__(self, value, comment=None):
        self.value = value
        self.comment = comment  # e.g. '  # Inline comment: greeting message'
    
    def __str__(self):
        # When converting to string for round-trip output, append the comment if present.
        if self.comment:
            return f'{self.value}{self.comment}'
        return str(self.value)
    
    def __repr__(self):
        return f"PreservedValue(value={self.value!r}, comment={self.comment!r})"

class PreservedArray(list):
    """
    Stores both the parsed items (as a list) and the original bracketed text,
    allowing both list access and perfect round-trip.
    """
    def __init__(self, items, original_text):
        super().__init__(items)
        self.origin = original_text  # the entire "[ ... ]" text

    def __eq__(self, other):
        if isinstance(other, list):
            return list(self) == other
        return super().__eq__(other)

    def __repr__(self):
        return f"PreservedArray({list(self)!r}, text={self.origin!r})"

    def __str__(self):
        return self.origin


class PreservedInlineTable(dict):
    """
    Subclass dict so code using it sees a normal dict,
    but store 'original_text' for exact round-trip.
    """
    def __init__(self, data, original_text):
        super().__init__(data)  # parse dict content
        self.origin = original_text

    def __repr__(self):
        return f"PreservedInlineTable(data={dict(self)}, text={self.origin!r})"

    def __str__(self):
        # Return the brace-delimited text exactly as originally parsed.
        return self.origin

