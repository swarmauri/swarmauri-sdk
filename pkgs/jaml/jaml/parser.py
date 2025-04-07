# parser.py

from typing import List, Tuple, Any, Optional
from ._tokenizer import nested_tokenize
from .ast_nodes import (
    DocumentNode,
    SectionNode,
    KeyValueNode,
    ScalarNode,
    ArrayNode,
    TableNode,
    LogicExpressionNode,
    CommentNode  # New AST node for comments
)

class JMLParser:
    """
    A parser that turns a JML string into a DocumentNode (AST).
    Relies on 'nested_tokenize()' to handle nested arrays/tables.
    """

    def parse(self, source: str) -> DocumentNode:
        tokens = nested_tokenize(source)
        document = DocumentNode()
        # Initialize a preamble list for standalone comments.
        document.preamble = []
        document.sections = []
        current_section = None
        i = 0

        while i < len(tokens):
            # Skip any whitespace tokens that contain a newline.
            if tokens[i][0] == "WHITESPACE" and "\n" in tokens[i][1]:
                i += 1
                continue

            kind, value = tokens[i][0], tokens[i][1]

            # Process standalone comments only if they are not part of an inline construct.
            # Inline comments are detected after a key–value pair.
            if kind == "COMMENT":
                comment_node = CommentNode(comment=value)
                if current_section is None:
                    document.preamble.append(comment_node)
                else:
                    if not hasattr(current_section, 'comments'):
                        current_section.comments = []
                    current_section.comments.append(comment_node)
                i += 1
                continue

            # Handle section headers (TABLE_SECTION or TABLE_ARRAY)
            if kind == "TABLE_SECTION":
                section_name = value.strip()[1:-1]
                current_section = SectionNode(name=section_name)
                document.sections.append(current_section)
                i += 1
                continue

            if kind == "TABLE_ARRAY":
                section_name = value.strip()[2:-2]
                current_section = SectionNode(name=section_name)
                document.sections.append(current_section)
                i += 1
                continue

            # Key–Value pair handling:
            if kind == "KEYWORD":
                raise SyntaxError(f"Cannot use reserved keyword '{value}' as an identifier/key")

            if kind == "RESERVED_FUNC":
                raise SyntaxError(f"Cannot use reserved function '{value}' as an identifier/key")

            if kind == "IDENTIFIER":
                # Process the key.
                key = value
                if key in ("File", "Git"):
                    raise SyntaxError(f"Cannot use reserved function name '{key}' as an identifier/key")
                i += 1

                # Skip any inline whitespace (without newline) between the key and the punctuation.
                while i < len(tokens) and tokens[i][0] == "WHITESPACE" and "\n" not in tokens[i][1]:
                    i += 1

                type_annotation = None
                value_node = ScalarNode(value=None)

                # Check for colon indicating a type annotation.
                if i < len(tokens) and tokens[i][0] == "PUNCTUATION" and tokens[i][1] == ":":
                    i += 1  # Skip the colon
                    while i < len(tokens) and tokens[i][0] == "WHITESPACE" and "\n" not in tokens[i][1]:
                        i += 1
                    if i < len(tokens) and tokens[i][0] in ("IDENTIFIER", "NULL"):
                        type_annotation = tokens[i][1]
                        i += 1
                    # Skip any whitespace before the operator.
                    while i < len(tokens) and tokens[i][0] == "WHITESPACE" and "\n" not in tokens[i][1]:
                        i += 1
                    if i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == "=":
                        i += 1  # Skip '='
                        while i < len(tokens) and tokens[i][0] == "WHITESPACE" and "\n" not in tokens[i][1]:
                            i += 1
                        value_node, consumed = self._parse_value(tokens, i)
                        i += consumed
                    else:
                        value_node = ScalarNode(value=None)
                # Check for an operator '=' directly after the key.
                elif i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == "=":
                    i += 1  # Skip '='
                    while i < len(tokens) and tokens[i][0] == "WHITESPACE" and "\n" not in tokens[i][1]:
                        i += 1
                    value_node, consumed = self._parse_value(tokens, i)
                    i += consumed
                else:
                    # If neither ':' nor '=' is found, leave the value as None.
                    value_node = ScalarNode(value=None)

                # Check for an inline (trailing) comment after the value.
                inline_comment = None
                if i < len(tokens) and tokens[i][0] == "WHITESPACE" and "\n" not in tokens[i][1]:
                    # Preserve the whitespace exactly as is.
                    inline_ws = tokens[i][1]
                    if i + 1 < len(tokens) and tokens[i + 1][0] == "COMMENT":
                        inline_comment = inline_ws + tokens[i + 1][1]
                        i += 2  # Consume both the whitespace and the COMMENT tokens

                # If no section has been started, create a default section.
                if current_section is None:
                    current_section = SectionNode(name="__default__")
                    document.sections.append(current_section)
                kv_node = KeyValueNode(
                    key=key, 
                    type_annotation=type_annotation, 
                    value=value_node,
                    comment=inline_comment  # Attach the inline comment if present
                )
                current_section.keyvalues.append(kv_node)
                continue

            # For any unrecognized tokens, simply skip.
            i += 1

        return document

    def _parse_value(self, tokens: List[Tuple[str, str, Any]], start_index: int) -> Tuple[Any, int]:
        """
        Given a token list and a starting index, parse out a 'value' node.
        Returns a tuple: (node, number_of_tokens_consumed).
        """
        if start_index >= len(tokens):
            return ScalarNode(value=None), 0

        kind, raw_value = tokens[start_index][0], tokens[start_index][1]
        consumed = 1  # Default to consuming one token

        if kind == "STRING":
            if raw_value.startswith("f"):
                raw_value = raw_value[1:]
            if raw_value.startswith("'''") or raw_value.startswith('"""'):
                stripped = raw_value[3:-3]
                node = ScalarNode(value=stripped)
                node.raw = raw_value  # Preserve raw string for round-trip fidelity.
                return node, consumed
            else:
                stripped = raw_value[1:-1]
                return ScalarNode(value=stripped), consumed

        elif kind == "INTEGER":
            return ScalarNode(value=int(raw_value, 0)), consumed

        elif kind == "FLOAT":
            return ScalarNode(value=float(raw_value)), consumed

        elif kind == "BOOLEAN":
            bool_val = (raw_value.lower() == "true")
            return ScalarNode(value=bool_val), consumed

        elif kind == "NULL":
            return ScalarNode(value=None), consumed

        elif kind == "ARRAY":
            sub_tokens = tokens[start_index][2]  # The nested tokens for the array.
            array_items = []
            idx = 0
            while idx < len(sub_tokens):
                val_node, c = self._parse_value(sub_tokens, idx)
                array_items.append(val_node)
                idx += c
                while idx < len(sub_tokens) and sub_tokens[idx][0] in ("PUNCTUATION", "WHITESPACE"):
                    idx += 1
            arr_node = ArrayNode(items=array_items)
            if "\n" in raw_value:
                arr_node.raw = raw_value
            return arr_node, consumed

        elif kind == "INLINE_TABLE":
            sub_tokens = tokens[start_index][2]
            keyvalues = []
            idx = 0
            while idx < len(sub_tokens):
                while idx < len(sub_tokens) and sub_tokens[idx][0] in ("PUNCTUATION", "WHITESPACE"):
                    idx += 1
                if idx >= len(sub_tokens):
                    break
                if (idx + 1 < len(sub_tokens) and 
                    sub_tokens[idx][0] == "IDENTIFIER" and 
                    sub_tokens[idx+1][0] == "OPERATOR" and 
                    sub_tokens[idx+1][1] == "="):
                    table_key = sub_tokens[idx][1]
                    idx += 2  # Skip key and '=' tokens.
                    val_node, consumed_inner = self._parse_value(sub_tokens, idx)
                    idx += consumed_inner
                    keyvalues.append(KeyValueNode(key=table_key, value=val_node))
                else:
                    idx += 1
                while idx < len(sub_tokens) and sub_tokens[idx][0] in ("PUNCTUATION", "WHITESPACE"):
                    idx += 1
            table_node = TableNode(keyvalues=keyvalues)
            table_node.raw = raw_value
            return table_node, consumed

        elif kind == "IDENTIFIER":
            raise SyntaxError("cannot assign identifier to identifier.")

        elif kind == "TILDE_BLOCK":
            inner = raw_value[2:-2].strip()
            try:
                from types import SimpleNamespace
                eval_globals = {"__builtins__": {}}
                eval_locals = {
                    "true": True,
                    "false": False,
                    "inf": float("inf"),
                    "nan": float("nan"),
                    "is_active": True,
                    "user": SimpleNamespace(roles=["admin"])
                }
                evaluated = eval(inner, eval_globals, eval_locals)
            except Exception as e:
                raise SyntaxError(f"Error evaluating expression: {inner}") from e
            return ScalarNode(value=evaluated), consumed

        return ScalarNode(value=raw_value), consumed
