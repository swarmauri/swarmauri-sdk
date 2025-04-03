# _helpers.py

from typing import Dict, List, Optional
from .ast_nodes import (
    DocumentNode,
    SectionNode,
    KeyValueNode,
    ScalarNode,
    ArrayNode,
    TableNode,
    LogicExpressionNode
)

def _process_table_merges(ast: DocumentNode) -> DocumentNode:
    """
    Processes any table-merge directives in the AST.
    For instance, if your JML uses syntax like:
    
        [my_section]
        merge << other_section

    This function finds that directive, looks up `other_section`,
    and merges all of its key-values into `my_section`.
    
    Modify the logic to match your JML merge semantics.
    
    :param ast: The DocumentNode AST to process.
    :return: The same AST (possibly modified in-place), with merges applied.
    """
    # 1) Build a dictionary mapping section_name -> SectionNode
    section_map: Dict[str, SectionNode] = {}
    for section in ast.sections:
        section_map[section.name] = section

    # 2) For each section, look for merges
    for section in ast.sections:
        # We'll collect new keyvalues to append at the end
        merges_to_apply: List[KeyValueNode] = []

        # We'll build a new list of keyvalues for the section
        # because we might remove the "merge" lines or do something with them.
        updated_keyvalues: List[KeyValueNode] = []

        for kv in section.keyvalues:
            # Example assumption:
            #   if kv.key == "merge" AND kv.value is a ScalarNode with a string:
            #   interpret that string as the name of another section to merge.
            #
            #   Or if you prefer an operator approach or a different key,
            #   adjust accordingly.

            if kv.key.lower() == "merge" and isinstance(kv.value, ScalarNode):
                merge_target_name = str(kv.value.value)
                # See if there's a corresponding section to merge with
                merge_target = section_map.get(merge_target_name)

                if merge_target:
                    # Extract the KVs from the target
                    merges_to_apply.extend(merge_target.keyvalues)
                # We might choose to omit the `merge` line from final output.
                # So we do NOT add this kv to updated_keyvalues.
            else:
                updated_keyvalues.append(kv)

        # 3) Perform the actual merges
        # By default, let's say we only add new keys that don't exist yet.
        # If you prefer overwriting, do it differently.
        for mkv in merges_to_apply:
            if not _contains_key(updated_keyvalues, mkv.key):
                updated_keyvalues.append(mkv)

        # 4) Replace the section's keyvalues with the updated list
        section.keyvalues = updated_keyvalues

    return ast

def _contains_key(kvs: List[KeyValueNode], key: str) -> bool:
    """
    Helper: checks if the given list of KeyValueNodes contains a node with .key == key
    """
    for kv in kvs:
        if kv.key == key:
            return True
    return False
