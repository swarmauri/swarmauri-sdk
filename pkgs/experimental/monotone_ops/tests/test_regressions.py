from dataclasses import dataclass

from monotone_ops.matrix import max_dilate, min_erode
from monotone_ops.ordering import argmax_by, argmin_by, earliest_by, latest_by, lexicographic_max


@dataclass
class Payload:
    score: int
    replica: int


def test_morphology_clipped_empty_boundary_neighborhood_keeps_cell():
    grid = ((1, 2), (3, 4))
    offsets = ((1, 0), (0, 1))

    assert max_dilate(grid, offsets) == ((3, 4), (4, 4))
    assert min_erode(grid, offsets) == ((2, 4), (4, 4))


def test_selectors_without_tie_key_do_not_compare_payloads():
    a = Payload(score=1, replica=1)
    b = Payload(score=1, replica=2)

    assert argmax_by(lambda item: item.score)(a, b) is a
    assert argmin_by(lambda item: item.score)(a, b) is a
    assert latest_by(lambda item: item.score)(a, b) is a
    assert earliest_by(lambda item: item.score)(a, b) is a
    assert lexicographic_max(lambda item: item.score)(a, b) is a


def test_selectors_with_tie_key_use_explicit_tie_breaker():
    a = Payload(score=1, replica=1)
    b = Payload(score=1, replica=2)

    assert argmax_by(lambda item: item.score, tie_key=lambda item: item.replica)(a, b) is b
    assert argmin_by(lambda item: item.score, tie_key=lambda item: item.replica)(a, b) is a
