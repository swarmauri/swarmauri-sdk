"""Graph operators under node/edge inclusion."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass

Node = Hashable
Edge = tuple[Node, Node]


@dataclass(frozen=True, slots=True)
class Graph:
    nodes: frozenset[Node]
    edges: frozenset[Edge]

    @staticmethod
    def from_edges(edges: Iterable[Edge]) -> Graph:
        edge_set = frozenset(edges)
        node_set = frozenset(x for edge in edge_set for x in edge)
        return Graph(node_set, edge_set)


def graph_leq(a: Graph, b: Graph) -> bool:
    return a.nodes <= b.nodes and a.edges <= b.edges


def graph_union(a: Graph, b: Graph) -> Graph:
    return Graph(a.nodes | b.nodes, a.edges | b.edges)


def graph_intersection(a: Graph, b: Graph) -> Graph:
    edges = a.edges & b.edges
    nodes = (a.nodes & b.nodes) | frozenset(x for edge in edges for x in edge)
    return Graph(nodes, edges)


def adjacency(graph: Graph) -> dict[Node, frozenset[Node]]:
    out: dict[Node, set[Node]] = {node: set() for node in graph.nodes}
    for src, dst in graph.edges:
        out.setdefault(src, set()).add(dst)
        out.setdefault(dst, set())
    return {node: frozenset(dst) for node, dst in out.items()}


def reachable(graph: Graph, sources: Iterable[Node]) -> frozenset[Node]:
    adj = adjacency(graph)
    seen = set(sources)
    frontier = list(seen)
    while frontier:
        node = frontier.pop()
        for nxt in adj.get(node, frozenset()):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return frozenset(seen)


def reverse_graph(graph: Graph) -> Graph:
    return Graph(graph.nodes, frozenset((dst, src) for src, dst in graph.edges))


def predecessors(graph: Graph, targets: Iterable[Node]) -> frozenset[Node]:
    return reachable(reverse_graph(graph), targets)


def transitive_closure_edges(graph: Graph, *, reflexive: bool = False) -> frozenset[Edge]:
    edges: set[Edge] = set()
    for node in graph.nodes:
        reach = reachable(graph, [node])
        if not reflexive:
            reach = frozenset(x for x in reach if x != node)
        edges.update((node, dst) for dst in reach)
    return frozenset(edges)


def transitive_closure_graph(graph: Graph, *, reflexive: bool = False) -> Graph:
    return Graph(graph.nodes, transitive_closure_edges(graph, reflexive=reflexive))


def undirected_closure(graph: Graph) -> Graph:
    """Add symmetric edges; monotone under edge inclusion."""

    reverse = frozenset((dst, src) for src, dst in graph.edges)
    return Graph(graph.nodes, graph.edges | reverse)


def component_labels(graph: Graph) -> dict[Node, frozenset[Node]]:
    """Connected-component map for an undirected interpretation of ``graph``."""

    undirected = undirected_closure(graph)
    return {node: reachable(undirected, [node]) for node in undirected.nodes}


def edge_cut(graph: Graph, allowed_nodes: frozenset[Node]) -> Graph:
    """Restrict to a fixed node subset. Monotone in graph inclusion."""

    edges = frozenset((u, v) for u, v in graph.edges if u in allowed_nodes and v in allowed_nodes)
    return Graph(graph.nodes & allowed_nodes, edges)


def from_adjacency(adj: Mapping[Node, Iterable[Node]]) -> Graph:
    edges = frozenset((src, dst) for src, dsts in adj.items() for dst in dsts)
    nodes = frozenset(adj.keys()) | frozenset(dst for _, dst in edges)
    return Graph(nodes, edges)


def path_counts_dag(graph: Graph, source: Node) -> dict[Node, int]:
    """Monotone dynamic-programming summary for DAGs with source count 1."""

    adj = adjacency(graph)
    indegree: dict[Node, int] = {node: 0 for node in graph.nodes}
    for _, dst in graph.edges:
        indegree[dst] = indegree.get(dst, 0) + 1
    queue = [node for node, degree in indegree.items() if degree == 0]
    counts: defaultdict[Node, int] = defaultdict(int)
    counts[source] = 1
    while queue:
        node = queue.pop(0)
        for dst in adj.get(node, frozenset()):
            counts[dst] += counts[node]
            indegree[dst] -= 1
            if indegree[dst] == 0:
                queue.append(dst)
    return dict(counts)
