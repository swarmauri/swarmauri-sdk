from monotone_ops.core import fold
from monotone_ops.collections import set_union
from monotone_ops.numeric import saturating_sum

facts = fold(set_union, [frozenset({"a"}), frozenset({"b"})])
score = fold(saturating_sum(10), [3, 4, 9])

assert facts == frozenset({"a", "b"})
assert score == 10
