import pytest

from swarmauri_matrix_hamming74 import Hamming74Matrix


def test_shape_is_fixed():
    matrix = Hamming74Matrix()
    assert matrix.shape == (4, 7)


def test_encode_known_message():
    matrix = Hamming74Matrix()
    message = [1, 0, 1, 1]
    assert matrix.encode(message) == [1, 0, 1, 1, 0, 1, 0]


def test_syndrome_detects_single_bit_error():
    matrix = Hamming74Matrix()
    codeword = matrix.encode([1, 1, 0, 1])
    corrupted = codeword.copy()
    corrupted[2] ^= 1
    syndrome = matrix.syndrome(corrupted)
    parity_columns = list(zip(*matrix.parity_check_matrix))
    assert syndrome in [list(column) for column in parity_columns]


def test_correct_recovers_single_bit_error():
    matrix = Hamming74Matrix()
    codeword = matrix.encode([0, 1, 1, 0])
    corrupted = codeword.copy()
    corrupted[5] ^= 1
    corrected = matrix.correct(corrupted)
    assert corrected == codeword


def test_distance_matches_metric():
    matrix = Hamming74Matrix()
    a = matrix.encode([1, 0, 0, 0])
    b = matrix.encode([0, 1, 0, 0])
    assert matrix.distance(a, b) == pytest.approx(4.0)


def test_minimum_distance_is_three():
    matrix = Hamming74Matrix()
    assert matrix.minimum_distance() == 3


def test_nearest_codeword_returns_closest_match():
    matrix = Hamming74Matrix()
    codeword = matrix.encode([1, 1, 1, 0])
    received = codeword.copy()
    received[0] ^= 1
    received[6] ^= 1
    nearest = matrix.nearest_codeword(received)
    assert nearest == matrix.correct(received)


def test_invalid_message_raises():
    matrix = Hamming74Matrix()
    with pytest.raises(ValueError):
        matrix.encode([1, 0, 1])
