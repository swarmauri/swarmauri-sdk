from collections import Counter

from monotone_ops.collections import counter_max, dict_join, set_subset_leq, set_union
from monotone_ops.core import fold, total_leq
from monotone_ops.information import CONFLICT, UNKNOWN, information_join, known
from monotone_ops.intervals import Interval, interval_hull, interval_leq, interval_widen
from monotone_ops.laws import (
    aci_reports,
    assert_all,
    check_associative,
    check_commutative,
    check_idempotent,
    check_monotone_binary,
)
from monotone_ops.numeric import Bounds, capped_max, saturating_sum


def test_set_union_aci_and_monotone():
    samples = [frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2})]
    assert_all(*aci_reports(set_union, samples))
    check_monotone_binary(set_union, set_subset_leq, samples).assert_ok()


def test_saturating_sum_associative_commutative_monotone():
    op = saturating_sum(10)
    samples = [0, 1, 3, 10]
    assert_all(check_associative(op, samples), check_commutative(op, samples))
    check_monotone_binary(op, total_leq, samples).assert_ok()


def test_capped_max_idempotent():
    op = capped_max(Bounds(0, 1))
    samples = [0, 0.5, 1]
    assert_all(check_idempotent(op, samples), check_commutative(op, samples))


def test_dict_join_pointwise_max():
    op = dict_join(max)
    assert op({"a": 1}, {"a": 3, "b": 2}) == {"a": 3, "b": 2}


def test_counter_max_join():
    assert counter_max(Counter(a=1), Counter(a=3, b=2)) == Counter(a=3, b=2)


def test_information_lattice():
    assert information_join(UNKNOWN, known("x")) == known("x")
    assert information_join(known("x"), known("x")) == known("x")
    assert information_join(known("x"), known("y")) == CONFLICT


def test_interval_join_widening():
    a = Interval(0, 1)
    b = Interval(-1, 3)
    assert interval_hull(a, b) == b
    assert interval_leq(a, b)
    assert interval_widen(a, b) == Interval(float("-inf"), float("inf"))


def test_fold_empty_and_initial():
    assert fold(set_union, []) is None
    assert fold(set_union, [frozenset({1})], initial=frozenset()) == frozenset({1})
