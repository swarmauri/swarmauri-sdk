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
    LogicExpressionNode
)

class JMLParser:
    """
    A parser that turns a JML string into a DocumentNode (AST).
    Internally relies on 'nested_tokenize()' to handle nested arrays/tables.
    
    Note:
      - This example is a simplified approach. 
      - For advanced grammar, merges, or logic expressions, you might need 
        a more robust parser (e.g., with a formal grammar or additional parsing phases).
    """

    def parse(self, source: str) -> DocumentNode:
        tokens = nested_tokenize(source)
        document = DocumentNode()
        current_section = None
        i = 0

        while i < len(tokens):
            kind, value = tokens[i][0], tokens[i][1]

            # 1) Skip comments
            if kind == "COMMENT":
                i += 1
                continue

            # 2) TABLE_SECTION / TABLE_ARRAY handling
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

            # 3) Key-Value Handling
            #    If we see something we interpret as a "key"
            if kind == "KEYWORD":
                # 'if', 'elif', 'else', etc. used as key => error
                raise SyntaxError(f"Cannot use reserved keyword '{value}' as an identifier/key")

            if kind == "RESERVED_FUNC":
                # 'File()', 'Git()' used as key => error
                raise SyntaxError(f"Cannot use reserved function '{value}' as an identifier/key")

            if kind == "IDENTIFIER":
                key = value
                if value in ("File", "Git"):
                    raise SyntaxError(f"Cannot use reserved function name '{value}' as an identifier/key")

                # Next tokens might be ':' or '='
                if (i + 1 < len(tokens)
                    and tokens[i + 1][0] == "PUNCTUATION"
                    and tokens[i + 1][1] == ":"):

                    # key: ...
                    i += 2  # skip 'IDENTIFIER' and ':' 
                    type_annotation = None

                    # Possibly parse a type annotation
                    if i < len(tokens) and tokens[i][0] == "IDENTIFIER":
                        type_annotation = tokens[i][1]
                        i += 1

                    # Check for '='
                    if i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == "=":
                        i += 1
                        value_node, consumed = self._parse_value(tokens, i)
                        i += consumed
                    else:
                        # No '=' => no value
                        value_node = ScalarNode(value=None)

                elif (i + 1 < len(tokens)
                      and tokens[i + 1][0] == "OPERATOR"
                      and tokens[i + 1][1] == "="):
                    # key = value
                    i += 2
                    type_annotation = None
                    value_node, consumed = self._parse_value(tokens, i)
                    i += consumed

                else:
                    # not recognized => skip
                    i += 1
                    type_annotation = None
                    value_node = ScalarNode(value=None)

                # create KeyValueNode
                if current_section is not None:
                    kv_node = KeyValueNode(
                        key=key, 
                        type_annotation=type_annotation, 
                        value=value_node
                    )
                    current_section.keyvalues.append(kv_node)
                else:
                    # no active section => either create one or error 
                    pass

                continue

            # If we get here, we haven't recognized the token => skip or handle
            i += 1

        return document


    def _parse_value(self, tokens: List[Tuple[str, str, Any]], start_index: int) -> Tuple[Any, int]:
        """
        Given a token list and a starting index, parse out a 'value' node.
        Returns a tuple: (node, number_of_tokens_consumed).

        This method handles:
          - STRING, INTEGER, FLOAT, BOOLEAN, NULL
          - ARRAY (plus sub-tokens)
          - INLINE_TABLE (plus sub-tokens)
          - Simple usage for IDENTIFIER (could be a reference or expression)
          - (Optional) logic expressions, merges, etc. if you want to expand.
        """
        if start_index >= len(tokens):
            return ScalarNode(value=None), 0

        kind, raw_value = tokens[start_index][0], tokens[start_index][1]
        consumed = 1  # default to consuming this single token

        if kind == "STRING":
            # Remove outer quotes. This is naive—improve as needed for escapes, etc.
            if len(raw_value) >= 2:
                stripped = raw_value[1:-1]
            else:
                stripped = ""
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
            # 'ARRAY' tokens from nested_tokenize() come with a third element:
            #   ( "ARRAY", "[ ... ]", [subtokens...] )
            sub_tokens = tokens[start_index][2]  # the nested tokens
            array_items = []
            idx = 0
            while idx < len(sub_tokens):
                # Attempt to parse each item
                val_node, c = self._parse_value(sub_tokens, idx)
                array_items.append(val_node)
                idx += c
                # skip punctuation (commas, etc.) or whitespace in between
                while (idx < len(sub_tokens) 
                       and sub_tokens[idx][0] in ("PUNCTUATION", "WHITESPACE")):
                    idx += 1

            arr_node = ArrayNode(items=array_items)
            return arr_node, consumed

        elif kind == "INLINE_TABLE":
            # Similar to ARRAY, we have a third element with sub-tokens
            sub_tokens = tokens[start_index][2]
            keyvalues = []
            idx = 0
            while idx < len(sub_tokens):
                # For example: mykey = "value", or mykey = 123
                if (idx + 1 < len(sub_tokens)
                    and sub_tokens[idx][0] == "IDENTIFIER"
                    and sub_tokens[idx+1][0] == "OPERATOR"
                    and sub_tokens[idx+1][1] == "="):
                    
                    table_key = sub_tokens[idx][1]  # the IDENTIFIER string
                    idx += 2  # skip the key and '='
                    
                    val_node, c = self._parse_value(sub_tokens, idx)
                    idx += c
                    keyvalues.append(KeyValueNode(key=table_key, value=val_node))
                else:
                    idx += 1

            table_node = TableNode(keyvalues=keyvalues)
            return table_node, consumed

        elif kind == "IDENTIFIER":
            # Could be a reference, function call, or logic expression. 
            # For simplicity, treat it as a string.
            return ScalarNode(value=raw_value), consumed

        elif kind == "TILDE_BLOCK":
            # Remove the delimiters: {~ and ~}
            inner = raw_value[2:-2].strip()
            try:
                # Use an empty dict for __builtins__ and supply required variables.
                eval_globals = {"__builtins__": {}}
                eval_locals = {
                    "true": True,
                    "false": False,
                    "inf": float("inf"),
                    "nan": float("nan"),
                    "is_active": True  # Supply is_active; adjust as needed.
                }
                evaluated = eval(inner, eval_globals, eval_locals)
            except Exception as e:
                raise SyntaxError(f"Error evaluating expression: {inner}") from e
            return ScalarNode(value=evaluated), consumed



        # --------------------------------------------------------------
        # In support of MEP-0015 & MEP-0022
        # (Optional) Additional branches for logic expressions, merges, 
        # or special functions could go here. e.g.:
        # 
        # elif kind == "KEYWORD" or kind == "RESERVED_FUNC":
        #     # handle logic or function calls
        #     ...
        # 
        # elif kind == "OPERATOR" and raw_value in ("<<",):
        #     # handle merges or references
        #     ...
        # --------------------------------------------------------------

        # Fallback
        return ScalarNode(value=raw_value), consumed
