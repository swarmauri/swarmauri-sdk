"""Graph utilities for dependency resolution."""

import heapq
from collections import defaultdict
from typing import Any, Dict, List


# development method, may be unstable
def get_immediate_dependencies(
    payload: List[Dict[str, Any]], target_file: str
) -> List[str]:
    """
    @dev development method, may be unstable

    ---

    Returns a list of files that `target_file` directly depends on (one‑hop parents).

    Args:
      payload: List of record dicts, each with "RENDERED_FILE_NAME" and EXTRAS["DEPENDENCIES"].
      target_file: The filename whose direct dependencies you want.

    Raises:
      ValueError: if `target_file` isn’t present in the payload.

    Returns:
      A list of filenames that `target_file` depends on directly.
    """
    # Build the forward graph to get all nodes
    forward_graph, _, all_nodes = _build_forward_graph(payload)
    if target_file not in all_nodes:
        raise ValueError(f"File '{target_file}' not found in payload.")
    # Invert to get direct dependency mapping
    reverse_graph = _build_reverse_graph(forward_graph)
    return reverse_graph[target_file]


def _build_forward_graph(payload: List[Dict[str, Any]]):
    """
    Builds a graph (adjacency list) and an in-degree map from the payload.
    An edge from Y to X indicates that file X depends on file Y.
    Returns:
      - forward_graph: dict[node, list of neighbors]  (Y -> X)
      - in_degree: dict[node, int]
      - all_nodes: set of all node names
    """
    forward_graph = defaultdict(list)
    in_degree = {}
    all_nodes = set(entry["RENDERED_FILE_NAME"] for entry in payload)
    # Initialize in_degree for every node.
    for node in all_nodes:
        in_degree[node] = 0

    # Build edges: (dep -> file)
    for entry in payload:
        file_node = entry["RENDERED_FILE_NAME"]
        extras = entry.get("EXTRAS", {})
        deps = extras.get("DEPENDENCIES", [])
        if deps:
            for dep in deps:
                # Only add the edge if the dependency also exists in our payload.
                if dep in all_nodes:
                    forward_graph[dep].append(file_node)
                    in_degree[file_node] += 1

    # Ensure every node appears in the adjacency list
    for node in all_nodes:
        if node not in forward_graph:
            forward_graph[node] = []

    return forward_graph, in_degree, all_nodes


def _build_reverse_graph(forward_graph: Dict[str, List[str]]):
    """
    Given the forward graph (dep -> file),
    build a reverse graph (file -> list of direct dependencies).
    """
    reverse_graph = defaultdict(list)
    for dep, neighbors in forward_graph.items():
        for file_node in neighbors:
            # In reverse, file_node -> dep
            reverse_graph[file_node].append(dep)

    # Ensure every node in forward_graph also appears in reverse_graph
    for node in forward_graph.keys():
        if node not in reverse_graph:
            reverse_graph[node] = []
    return reverse_graph


def _topological_sort(payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Returns a list of entries sorted so that if file A depends on file B,
    then B comes before A. Raises an Exception if cyclic or missing dependencies are detected.
    Ensures that ties (same in-degree) are broken alphabetically by file name.
    """
    forward_graph, in_degree, _ = _build_forward_graph(payload)
    sorted_names = []

    # Use a min-heap to ensure alphabetical processing of all nodes that have in_degree = 0.
    zero_in_degree = [node for node, deg in in_degree.items() if deg == 0]
    heapq.heapify(zero_in_degree)

    while zero_in_degree:
        # Always pop the lexicographically smallest name first.
        node = heapq.heappop(zero_in_degree)
        sorted_names.append(node)
        for neighbor in forward_graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(zero_in_degree, neighbor)

    # Check if all nodes were sorted (detect cycles or references to missing dependencies).
    if len(sorted_names) != len(in_degree):
        leftovers = [n for n, deg in in_degree.items() if deg > 0]
        hint = ", ".join(sorted(leftovers))
        raise ValueError(f"Cyclic dependencies detected among file entries: {hint}")

    # Map sorted file names back to their payload records.
    entry_map = {e["RENDERED_FILE_NAME"]: e for e in payload}
    sorted_entries = [entry_map[name] for name in sorted_names]
    return sorted_entries


def _get_transitive_dependencies(
    target_file: str, reverse_graph: Dict[str, List[str]]
) -> set:
    """
    Returns a set of all files (including `target_file` itself)
    that are transitive dependencies leading to `target_file`.
    This uses the reverse graph, where edges are:
       file_node -> [list_of_its_direct_dependencies]
    """
    visited = set()
    stack = [target_file]

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            # For everything node depends on, keep going backward
            stack.extend(reverse_graph[node])
    return visited


def _transitive_dependency_sort(
    payload: List[Dict[str, Any]], target_file: str
) -> List[Dict[str, Any]]:
    """
    Return a topologically-sorted list of *only* those files
    that are transitive dependencies for `target_file` (plus `target_file` itself).
    """
    # First build the forward graph, etc.
    forward_graph, in_degree, all_nodes = _build_forward_graph(payload)
    if target_file not in all_nodes:
        raise ValueError(f"File '{target_file}' not found in payload.")

    # Build the reverse graph
    reverse_graph = _build_reverse_graph(forward_graph)

    # Get all files that target_file depends on (and target_file itself)
    dep_set = _get_transitive_dependencies(target_file, reverse_graph)

    # Filter payload to just those in dep_set
    sub_payload = [rec for rec in payload if rec["RENDERED_FILE_NAME"] in dep_set]

    # Finally, run a normal topological sort on the sub-payload
    return _topological_sort(sub_payload)
