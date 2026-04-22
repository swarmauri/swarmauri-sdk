# Research catalog: monotone operator families

Monotonicity is relative to an order. A unary operator `f` is monotone when
`x <= y` implies `f(x) <= f(y)`. A binary operator `op` is monotone when it is
monotone in each coordinate, or equivalently when `(a1 <= a2 and b1 <= b2)`
implies `op(a1, b1) <= op(a2, b2)` for product orders.

The most operationally useful merge operators are ACI: associative,
commutative, and idempotent. ACI operators tolerate batching, retries,
reordering, and duplicate delivery.

## Extended taxonomy

1. **Trivial and structural maps**
   - identity, constants, projections, composition, product lifts.
   - These are useful for building larger monotone pipelines from smaller maps.

2. **Join/meet semilattices**
   - set union/intersection, boolean OR/AND, numeric max/min, bit OR/AND.
   - Dict, tuple, matrix, and record forms are pointwise lifts of these operators.

3. **Ordered selectors**
   - argmax/argmin, latest-by-logical-clock, lexicographic max/min.
   - Deterministic tie keys turn total preorders into stable ACI selectors.

4. **Numeric accumulators**
   - nonnegative sum, nonnegative product, saturating sum, positive linear maps,
     quantizers, increasing affine maps, smooth caps.
   - These are monotone; only some are ACI. Use law tests to classify intended use.

5. **Positive Boolean operators**
   - monotone CNF/DNF, threshold, majority, any/all.
   - Monotone Boolean functions are expressible by positive formulas without negation.

6. **Information-order lattices**
   - unknown/known/conflict, partial-record completion, support/provenance union.
   - Useful for SSOT systems where disagreement must not be hidden by overwrite.

7. **Evidence and certification operators**
   - quorum sets, weighted quorum with duplicate-safe pointwise max, claim support,
     scorecards, threshold-derived predicates.
   - Keep state monotone; derive certification predicates from state.

8. **State-based CRDTs**
   - G-Set, 2P-Set, G-Counter, PN-Counter, OR-Set, vector clocks, LWW register as a
     timestamped lattice.
   - Merge computes a semilattice join; query/read views may be non-monotone.

9. **Abstract interpretation domains**
   - interval hull/intersection, interval widening/narrowing, sign lattice, taint lattice,
     finite powerset abstractions.
   - Widenings are convergence accelerators and should be treated differently from ACI joins.

10. **Closure/interior/fixpoint operators**
    - reachability closure, rule closure, Moore closure, Alexandrov interior, Galois-induced
      closure and interior, least fixpoint iteration.
    - Positive inference systems are typically least-fixpoint computations over powersets.

11. **Graph operators**
    - graph union/intersection, reachability, transitive closure, predecessor closure,
      undirected closure, component summaries.
    - Ordered by node/edge inclusion.

12. **Positive relational algebra**
    - union, selection by fixed predicate, projection, product, natural join, semijoin,
      positive consequence closure.
    - Difference and unrestricted negation are not monotone in all arguments.

13. **Semiring and path-algebra operators**
    - Boolean reachability, tropical min-plus shortest path, max-plus longest path on DAGs,
      max-min widest path, Viterbi max-product path.
    - Generic algorithms separate graph traversal from algebraic choice/composition.

14. **Sequence and stream orders**
    - append under prefix order, longest common prefix as meet, ordered dedup union,
      cumulative joins.
    - Sequence monotonicity depends strongly on whether the order is prefix, subsequence,
      lexicographic, or set-of-elements.

15. **Matrix/grid/image operators**
    - entrywise max/min/add, monotone dilation and erosion filters.
    - Ordered entrywise; morphology filters are monotone because max/min preserve order.

16. **Probability and score operators**
    - confidence max/min, noisy-or, independent product, logaddexp, bounded evidence sum.
    - Floating point can break exact algebraic equalities, so tests use deterministic examples.

17. **Security and policy lattices**
    - confidentiality label join, integrity duals, restrictive access-decision join,
      permission bitset union/intersection, risk max, trust min.
    - The order must be explicit: permissiveness and restrictiveness are dual orders.

18. **Galois and closure-derived operators**
    - abstraction/concretization pairs induce concrete closures and abstract interiors.
    - This is the bridge between concrete state spaces and tractable abstract domains.

## Non-monotone or order-sensitive traps

- subtraction is not monotone in its second argument under usual numeric order.
- arbitrary overwrite is not a semilattice merge.
- arrival-time last-write-wins is not deterministic under reordering; use logical clocks.
- average is monotone in numeric arguments but not associative as a merge.
- relation difference and negation are anti-monotone in the subtracted/negated relation.
- deleting from a set is not monotone under subset order; model removals as growing tombstones.
