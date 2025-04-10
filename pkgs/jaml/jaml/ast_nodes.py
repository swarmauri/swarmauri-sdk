import re
from ._helpers import (
    unquote, 
    resolve_scoped_variable, 
    evaluate_f_string, 
    evaluate_f_string_interpolation,
    evaluate_immediate_expression,
    evaluate_comprehension
)  

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
    def original(self) -> str:
        """Getter for the original text."""
        return self._original

    @original.setter
    def original(self, new_text):
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
        return f"FoldedExpressionNode(original={self._original!r}, content_tree={self.content_tree!r})"

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
    def original(self):
        return self.text

    @original.setter
    def original(self, value):
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


class DeferredExpression:
    def __init__(self, expr, local_env=None, original_text=None):
        self.expr = expr  # e.g., "'Yes' if true else 'No'"
        self.local_env = local_env or {}
        self.original = original_text  # e.g., "<{'Yes' if true else 'No'}>"

    def evaluate(self, global_env):
        env = {}
        env.update(global_env)
        env.update(self.local_env)

        substituted = evaluate_immediate_expression(self.expr, {}, env)
        try:
            return eval(substituted, {"__builtins__": {}}, {"true": True, "false": False})
        except Exception:
            return self.expr

    def __str__(self):
        # Return the exact text for round-trip 
        return self.original or f"<{{ {self.expr} }}>"

    def __repr__(self):
        return f"DeferredExpression(expr={self.expr!r}, local_env={self.local_env!r}, original={self.original!r})"

    def __eq__(self, other):
        if isinstance(other, str):
            # Compare with original literal
            return (self.original == other) if self.original else (f"<{{ {self.expr} }}>" == other)
        if isinstance(other, DeferredExpression):
            return (
                self.expr == other.expr 
                and self.local_env == other.local_env 
                and self.original == other.original
            )
        return False


class DeferredDictComprehension:
    def __init__(self, text):
        self.original_text = text  # The raw inner text, or full text including braces

    @property
    def original(self):
        return self.original_text

    @original.setter
    def original(self, value):
        self.original_text = value

    def evaluate(self, env):
        # (Your existing implementation that uses self.original_text.)
        pattern = r'^(f["\'].*?["\'])\s*(?::|=)\s*(.*?)\s+for\s+(\w+)\s+in\s+(.*)$'
        m = re.match(pattern, self.original_text.strip().strip('{}'))
        if not m:
            return self.original_text
        key_expr_str, val_expr_str, loop_var, iterable_str = m.groups()
        try:
            iterable = eval(iterable_str, {"__builtins__": {}}, env)
        except Exception:
            return self.original_text
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
        return "{" + self.original_text + "}"
    def __repr__(self):
        return f"DeferredDictComprehension({self.original_text!r})"
    def __eq__(self, other):
        if isinstance(other, str):
            return self.original_text == other
        if isinstance(other, DeferredDictComprehension):
            return self.original_text == other.original_text
        return False


class PreservedString(str):
    def __new__(cls, value, original):
        # Create a new string instance using the unquoted value.
        obj = super().__new__(cls, value)
        obj.value = value
        obj.original = original  # store the original text, e.g. '"Hello, World!"'
        return obj

    def __str__(self):
        # When converting to string for round-trip output, return the original quoted text.
        return self.original

    def __repr__(self):
        return f"PreservedString(value={super().__str__()!r}, original={self.original!r})"

    def __reduce_ex__(self, protocol):
        """
        Tells pickle/deepcopy how to re-create a PreservedString instance.
        Returns (constructor, args) so that __new__ is called correctly.
        """
        return (
            self.__class__,
            (self.value, self.original)  # The args we pass to __new__
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
        self.original_text = original_text  # the entire "[ ... ]" text

    def __eq__(self, other):
        if isinstance(other, list):
            return list(self) == other
        return super().__eq__(other)

    def __repr__(self):
        return f"PreservedArray({list(self)!r}, text={self.original_text!r})"

    def __str__(self):
        return self.original_text


class PreservedInlineTable(dict):
    """
    Subclass dict so code using it sees a normal dict,
    but store 'original_text' for exact round-trip.
    """
    def __init__(self, data, original_text):
        super().__init__(data)  # parse dict content
        self.original_text = original_text

    def __repr__(self):
        return f"PreservedInlineTable(data={dict(self)}, text={self.original_text!r})"

    def __str__(self):
        # Return the brace-delimited text exactly as originally parsed.
        return self.original_text

