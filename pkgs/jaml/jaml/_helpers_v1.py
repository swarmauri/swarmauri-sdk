from .ast_nodes import (
    DocumentNode,
    SectionNode,
    KeyValueNode,
    ScalarNode,
    ArrayNode,
    TableNode,
    LogicExpressionNode,
)
from ._operators import _ANCHOR_KEY, _CONTEXT_KEY
def _find_table_in_ast(ast: DocumentNode, ref_path: str):
    parts = ref_path.split('.')
    if len(parts) != 2:
        return None
    section_name, key_name = parts
    for sec in ast.sections:
        if sec.name == section_name:
            for kv in sec.keyvalues:
                if kv.key == key_name and isinstance(kv.value, TableNode):
                    return kv.value
    return None

def _process_table_merges(ast: DocumentNode) -> DocumentNode:
    for section in ast.sections:
        for kv in section.keyvalues:
            if kv.type_annotation == "table" and isinstance(kv.value, TableNode):
                table_node = kv.value
                merge_nodes = [
                    node for node in table_node.keyvalues
                    if node.key == "<<" and node.type_annotation == "merge"
                ]
                if not merge_nodes:
                    continue

                current_items = {
                    node.key: node
                    for node in table_node.keyvalues
                    if node.key != "<<"
                }
                for merge_node in merge_nodes:
                    merge_ref = merge_node.value.value
                    if isinstance(merge_ref, str):
                        if merge_ref.startswith(_ANCHOR_KEY) or merge_ref.startswith(_CONTEXT_KEY):
                            ref_path = merge_ref[1:].strip()
                        else:
                            ref_path = merge_ref.strip()
                        source_table = _find_table_in_ast(ast, ref_path)
                        if source_table:
                            for src_kv in source_table.keyvalues:
                                if src_kv.key not in current_items:
                                    current_items[src_kv.key] = src_kv
                table_node.keyvalues = list(current_items.values())
    return ast

def _split_top_level_commas(s: str) -> list[str]:
    parts = []
    current = []
    brace_level = 0
    bracket_level = 0
    in_quotes = None

    for char in s:
        if in_quotes:
            current.append(char)
            if char == in_quotes:
                in_quotes = None
        else:
            if char in ('"', "'"):
                in_quotes = char
                current.append(char)
            elif char == '{':
                brace_level += 1
                current.append(char)
            elif char == '}':
                brace_level -= 1
                current.append(char)
            elif char == '[':
                bracket_level += 1
                current.append(char)
            elif char == ']':
                bracket_level -= 1
                current.append(char)
            elif char == ',' and brace_level == 0 and bracket_level == 0:
                part_str = "".join(current).strip()
                if part_str:
                    parts.append(part_str)
                current = []
            else:
                current.append(char)
    # Final piece
    part_str = "".join(current).strip()
    if part_str:
        parts.append(part_str)
    return parts
