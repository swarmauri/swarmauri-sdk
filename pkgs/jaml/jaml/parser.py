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
        """
        Parses the JML source string into a DocumentNode AST.
        
        1) Tokenizes the source (with nested brackets) via nested_tokenize().
        2) Iterates over tokens, creating SectionNodes and KeyValueNodes.
        3) Delegates parsing of values (strings, arrays, inline tables, etc.) 
           to the helper method '_parse_value'.
        4) Returns a DocumentNode that contains zero or more sections.
        """
        tokens = nested_tokenize(source)
        document = DocumentNode()
        current_section = None

        i = 0
        while i < len(tokens):
            kind, value = tokens[i][0], tokens[i][1]

            # ------------------------------------------------------
            # Skip comments and whitespace (if any remain)
            # ------------------------------------------------------
            if kind == "COMMENT":
                i += 1
                continue

            # ------------------------------------------------------
            # TABLE_SECTION: e.g. [section_name]
            # ------------------------------------------------------
            if kind == "TABLE_SECTION":
                section_name = value.strip()[1:-1]  # remove '[' and ']'
                current_section = SectionNode(name=section_name)
                document.sections.append(current_section)
                i += 1
                continue

            # ------------------------------------------------------
            # TABLE_ARRAY: e.g. [[section_name]]
            #
            # For a simple parser, treat [[section]] like just another section,
            # or store a flag if needed. 
            # ------------------------------------------------------
            if kind == "TABLE_ARRAY":
                section_name = value.strip()[2:-2]  # remove '[[' and ']]'
                current_section = SectionNode(name=section_name)
                document.sections.append(current_section)
                i += 1
                continue

            # ------------------------------------------------------
            # Potential key-value line:
            #   key: type_annotation = value
            #   key: = value
            #   key = value
            #   ...
            # ------------------------------------------------------
            if kind == "IDENTIFIER":
                key = value  # e.g. "mykey"

                # We look ahead to see whether the next tokens match a pattern
                # like ':' or '=' etc. This is fairly naive and can be improved.
                #
                # Example lines:
                #   foo: int = 42
                #   foo: = "string"
                #   foo = true

                # Check next token(s), if any
                if (i + 1 < len(tokens)
                    and tokens[i + 1][0] == "PUNCTUATION"
                    and tokens[i + 1][1] == ":"):
                    
                    # Pattern: key: ...
                    i += 2  # Skip the key and the ':'
                    type_annotation = None

                    # Possibly parse a type annotation if the next token 
                    # is an IDENTIFIER (like "int", "str", etc.).
                    if i < len(tokens) and tokens[i][0] == "IDENTIFIER":
                        # interpret it as a type annotation
                        type_annotation = tokens[i][1]
                        i += 1  # consume the type annotation

                    # Next token might be '=' or something else
                    if i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == "=":
                        i += 1  # consume '='
                        value_node, consumed = self._parse_value(tokens, i)
                        i += consumed
                    else:
                        # No '=' or no value
                        value_node = ScalarNode(value=None)

                elif (i + 1 < len(tokens)
                      and tokens[i + 1][0] == "OPERATOR"
                      and tokens[i + 1][1] == "="):
                    # Pattern: key = value
                    i += 2  # Skip 'key' and '='
                    type_annotation = None
                    value_node, consumed = self._parse_value(tokens, i)
                    i += consumed

                else:
                    # If it's not recognized as a key-value pattern,
                    # treat it as a key with no value or skip.
                    i += 1
                    type_annotation = None
                    value_node = ScalarNode(value=None)

                # Create KeyValueNode if we're in a valid section
                if current_section is not None:
                    kv_node = KeyValueNode(key=key, type_annotation=type_annotation, value=value_node)
                    current_section.keyvalues.append(kv_node)
                else:
                    # If not inside any section, you might:
                    # 1) create a default unnamed section, or
                    # 2) raise an error, etc.
                    pass

                continue

            # If we reach here, just move on.
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
            return ScalarNode(value=int(raw_value)), consumed

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

        # --------------------------------------------------------------
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
