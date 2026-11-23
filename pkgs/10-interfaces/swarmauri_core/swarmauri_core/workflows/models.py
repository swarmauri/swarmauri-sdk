"""Versioned graph structure and service bindings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NodeDefinition:
    """Bind a graph-local node to a service-registry name."""

    node_id: str
    service: str


@dataclass(frozen=True)
class EdgeDefinition:
    """Connect graph nodes without granting authority."""

    edge_id: str
    source: str
    target: str


@dataclass(frozen=True)
class GraphDefinition:
    """Describe a graph independently of scheduling or transport."""

    graph_id: str
    version: str
    nodes: tuple[NodeDefinition, ...]
    edges: tuple[EdgeDefinition, ...]

    def __post_init__(self):
        ids = [n.node_id for n in self.nodes]
        edge_ids = [e.edge_id for e in self.edges]
        if len(ids) != len(set(ids)) or len(edge_ids) != len(set(edge_ids)):
            raise ValueError("Graph identifiers must be unique")
        if any(e.source not in ids or e.target not in ids for e in self.edges):
            raise ValueError("Edge references an unknown node")

    def edge(self, edge_id: str) -> EdgeDefinition:
        for edge in self.edges:
            if edge.edge_id == edge_id:
                return edge
        raise KeyError(edge_id)


@dataclass(frozen=True)
class ServiceBinding:
    """Validate service details obtained through IServiceRegistry."""

    service: str
    subject: str
    audience: str
    endpoint: str
    protocol: str = "local"

    def __post_init__(self):
        if not all((self.service, self.subject, self.audience, self.endpoint)):
            raise ValueError("Service binding fields must be non-empty")
        if self.protocol not in {"local", "http"}:
            raise ValueError("Unsupported invocation protocol")
