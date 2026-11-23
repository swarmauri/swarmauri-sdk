from __future__ import annotations

from monotone_ops.semiring import algebraic_path_closure, tropical_min_plus

nodes = ["a", "b", "c"]
edges = {("a", "b"): 2.0, ("b", "c"): 3.0, ("a", "c"): 10.0}
dist = algebraic_path_closure(nodes, edges, tropical_min_plus())

print(dist[("a", "c")])
