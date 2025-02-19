"""
graph.py

This module provides functions to build and process a dependency graph from file records.
It includes functions to:
  - Build the forward dependency graph and compute in-degree counts.
  - Perform topological sorting on file records.
  - Find a start node in the sorted records based on provided selection parameters.
  - Process nodes from the identified start node onward.

Each file record is expected to have a unique identifier in the key "RENDERED_FILE_NAME"
and a list of resolved dependency identifiers in "RENDERED_DEPENDENCIES".
"""
from pprint import pprint
from typing import List, Dict, Tuple, Any
from collections import defaultdict, deque

def _topological_sort(payload):
    """
    Returns a list of entries sorted so that if file A depends on file B,
    then B comes before A. Raises an Exception if cyclic or missing dependencies are detected.
    """
    graph, in_degree = _build_forward_graph(payload)
    sorted_names = []
    # Start with nodes that have no dependencies.
    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    while queue:
        node = queue.popleft()
        sorted_names.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check if all nodes were sorted.
    if len(sorted_names) != len(in_degree):
        raise Exception("Cyclic or missing dependencies detected among file entries.")

    # Map sorted file names back to their payload records.
    entry_map = {e["RENDERED_FILE_NAME"]: e for e in payload}
    sorted_entries = [entry_map[name] for name in sorted_names]
    return sorted_entries


def _build_forward_graph(payload):
    """
    Builds a graph (adjacency list) and an in-degree map from the payload.
    An edge from Y to X indicates that file X depends on file Y.
    """
    graph = defaultdict(list)
    in_degree = {}
    # Initialize in_degree for all nodes using their rendered file names.
    all_nodes = set(entry["RENDERED_FILE_NAME"] for entry in payload)
    for node in all_nodes:
        in_degree[node] = 0

    # For each file entry, add an edge for each dependency.
    for entry in payload:
        file_node = entry["RENDERED_FILE_NAME"]
        for dep in entry.get("DEPENDENCIES", []):
            # Only add dependency if the dependent file exists in our payload.
            if dep in all_nodes:
                graph[dep].append(file_node)
                in_degree[file_node] += 1
            else:
                print(f"[WARNING] Dependency '{dep}' for file '{file_node}' not found among all nodes.")

    # Ensure every node appears in the graph.
    for node in all_nodes:
        if node not in graph:
            graph[node] = []

    return graph, in_degree


def _find_start_node(sorted_records: List[Dict[str, Any]], start_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Searches the sorted file records to locate the starting node based on the provided parameters.
    The start_params dictionary may include keys such as 'project', 'package', 'module', or 'file'.
    For instance, 'package' would match the package name in the record's PKG attribute, and 'file'
    would match the RENDERED_FILE_NAME.

    Parameters:
      sorted_records (List[Dict[str, Any]]): The topologically sorted file records.
      start_params (Dict[str, Any]): Dictionary with keys like 'project', 'package', 'module', 'file'.

    Returns:
      Dict[str, Any]: The matching file record, or None if not found.
    """
    for record in sorted_records:
        match = True
        for key, value in start_params.items():
            if key == "project":
                # Assuming project name is stored in record["NAME"].
                if record.get("NAME") != value:
                    match = False
                    break
            elif key == "package":
                if record.get("PKG", {}).get("NAME") != value:
                    match = False
                    break
            elif key == "module":
                if record.get("MOD", {}).get("NAME") != value:
                    match = False
                    break
            elif key == "file":
                if record.get("RENDERED_FILE_NAME") != value:
                    match = False
                    break
        if match:
            return record
    return None


def _process_from_node(start_node: Dict[str, Any], sorted_records: List[Dict[str, Any]]) -> None:
    """
    Processes the file records in order, starting from the specified start_node.
    This function iterates through the sorted_records from the index of start_node onward,
    processing each file accordingly.

    Parameters:
      start_node (Dict[str, Any]): The file record from which to start processing.
      sorted_records (List[Dict[str, Any]]): The topologically sorted file records.

    Returns:
      None
    """
    try:
        start_index = next(i for i, record in enumerate(sorted_records)
                           if record.get("RENDERED_FILE_NAME") == start_node.get("RENDERED_FILE_NAME"))
    except StopIteration:
        print("[ERROR] Start node not found in sorted records.")
        return

    # Process each file record from the starting index.
    for record in sorted_records[start_index:]:
        # Here, we assume that an external processing method (e.g., from processing.py) is invoked.
        # For demonstration purposes, we print the identifier.
        print(f"Processing file: {record.get('RENDERED_FILE_NAME')}")
        # In a complete implementation, you might call:
        # _process_file(record, global_attrs, template_dir)
