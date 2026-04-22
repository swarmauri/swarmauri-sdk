from monotone_ops.abstract import Sign, Taint, sign_add, sign_join, taint_join
from monotone_ops.crdt import (
    GCounter,
    GSet,
    ORSet,
    gcounter_merge,
    gset_merge,
    orset_merge,
    vector_clock_join,
)
from monotone_ops.evidence import (
    ClaimEvidence,
    QuorumState,
    certified_claims,
    claim_evidence_merge,
    quorum_merge,
)
from monotone_ops.graph import Graph, graph_union, reachable, transitive_closure_edges
from monotone_ops.relational import NamedRelation, named_project, natural_join, positive_consequence
from monotone_ops.semiring import algebraic_path_closure, boolean_semiring, tropical_min_plus


def test_abstract_domains():
    assert sign_join(Sign.NEG, Sign.ZERO) == Sign.NONPOS
    assert sign_add(Sign.POS, Sign.NEG) == Sign.TOP
    assert taint_join(Taint.CLEAN, Taint.TAINTED) == Taint.TAINTED


def test_crdt_merges():
    assert gset_merge(GSet(frozenset({1})), GSet(frozenset({2}))).members == frozenset({1, 2})
    assert vector_clock_join({"a": 1}, {"a": 0, "b": 2}) == {"a": 1, "b": 2}
    a = GCounter({"r1": 2})
    b = GCounter({"r1": 1, "r2": 3})
    assert gcounter_merge(a, b).value == 5
    s1 = ORSet({}, {}).add("x", "r1:1")
    s2 = ORSet({}, {}).add("x", "r2:1")
    assert orset_merge(s1, s2).value == frozenset({"x"})


def test_evidence():
    q = quorum_merge(QuorumState(frozenset({"a"})), QuorumState(frozenset({"b"})))
    assert q.reached(2)
    c = claim_evidence_merge(
        ClaimEvidence({"claim": frozenset({"a"})}),
        ClaimEvidence({"claim": frozenset({"b"})}),
    )
    assert certified_claims(c, 2) == frozenset({"claim"})


def test_graph_closure():
    g = Graph.from_edges([("a", "b"), ("b", "c")])
    assert reachable(g, ["a"]) == frozenset({"a", "b", "c"})
    assert ("a", "c") in transitive_closure_edges(g)
    assert graph_union(g, Graph.from_edges([("c", "d")])).nodes == frozenset({"a", "b", "c", "d"})


def test_relational_positive_rule():
    edges = NamedRelation(("x", "y"), frozenset({("a", "b"), ("b", "c")}))

    def rule(paths: NamedRelation) -> NamedRelation:
        joined = natural_join(paths, NamedRelation(("y", "z"), edges.rows))
        return NamedRelation(("x", "y"), frozenset((x, z) for x, _, z in joined.rows))

    closure = positive_consequence(edges, rule)
    assert ("a", "c") in closure.rows
    assert named_project(closure, ["x"]).schema == ("x",)


def test_semiring_paths():
    nodes = ["a", "b", "c"]
    edges = {("a", "b"): 2.0, ("b", "c"): 3.0, ("a", "c"): 10.0}
    dist = algebraic_path_closure(nodes, edges, tropical_min_plus())
    assert dist[("a", "c")] == 5.0
    reach = algebraic_path_closure(nodes, {("a", "b"): True, ("b", "c"): True}, boolean_semiring())
    assert reach[("a", "c")] is True
