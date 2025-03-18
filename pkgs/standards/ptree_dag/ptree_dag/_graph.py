import heapq
from typing import List, Dict, Any
from collections import defaultdict

def _topological_sort(payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Returns a list of entries sorted so that if file A depends on file B,
    then B comes before A. Raises an Exception if cyclic or missing dependencies are detected.
    Ensures that ties (same in-degree) are broken alphabetically by file name.
    """
    graph, in_degree = _build_forward_graph(payload)
    sorted_names = []

    # Use a min-heap to ensure alphabetical processing of all nodes that have in_degree = 0.
    zero_in_degree = [node for node, deg in in_degree.items() if deg == 0]
    heapq.heapify(zero_in_degree)

    while zero_in_degree:
        # Always pop the lexicographically smallest name first.
        node = heapq.heappop(zero_in_degree)
        sorted_names.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(zero_in_degree, neighbor)

    # Check if all nodes were sorted (detect cycles or references to missing dependencies).
    if len(sorted_names) != len(in_degree):
        raise Exception("Cyclic or missing dependencies detected among file entries.")

    # Map sorted file names back to their payload records.
    entry_map = {e["RENDERED_FILE_NAME"]: e for e in payload}
    sorted_entries = [entry_map[name] for name in sorted_names]
    return sorted_entries


def _build_forward_graph(payload: List[Dict[str, Any]]):
    """
    Builds a graph (adjacency list) and an in-degree map from the payload.
    An edge from Y to X indicates that file X depends on file Y.
    """
    graph = defaultdict(list)
    in_degree = {}
    all_nodes = set(entry["RENDERED_FILE_NAME"] for entry in payload)

    # Initialize in_degree for every node.
    for node in all_nodes:
        in_degree[node] = 0

    # Build edges based on DEPENDENCIES.
    for entry in payload:
        file_node = entry["RENDERED_FILE_NAME"]
        for dep in entry.get("DEPENDENCIES", []):
            # Only add the edge if the dependency also exists in our payload.
            if dep in all_nodes:
                graph[dep].append(file_node)
                in_degree[file_node] += 1

    # Ensure every node shows up in the adjacency list, even if it has no outgoing edges.
    for node in all_nodes:
        if node not in graph:
            graph[node] = []

    return graph, in_degree
