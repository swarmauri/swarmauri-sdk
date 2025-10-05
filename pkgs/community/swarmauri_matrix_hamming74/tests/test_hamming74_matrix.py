import numpy as np
import pytest

from swarmauri_matrix_hamming74 import Hamming74Matrix


def test_default_shape_and_generator_matrix():
    matrix = Hamming74Matrix()
    assert matrix.shape == (4, 7)
    expected_generator = np.array(
        [
            [1, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1],
        ],
        dtype=int,
    )
    np.testing.assert_array_equal(matrix.generator_matrix, expected_generator)


def test_encode_and_syndrome_detection():
    matrix = Hamming74Matrix()
    message = [1, 0, 1, 1]
    codeword = matrix.encode(message)
    assert codeword == [1, 0, 1, 1, 0, 1, 0]

    errored = codeword.copy()
    errored[4] ^= 1
    assert matrix.syndrome(errored) == [1, 0, 0]


def test_nearest_codeword_corrects_single_error():
    matrix = Hamming74Matrix()
    codeword = matrix.encode([0, 1, 1, 0])
    errored = codeword.copy()
    errored[2] ^= 1
    assert matrix.nearest_codeword(errored) == codeword


def test_decode_returns_message_and_codeword():
    matrix = Hamming74Matrix()
    codeword = matrix.encode([1, 1, 0, 0])
    errored = codeword.copy()
    errored[6] ^= 1
    message, corrected = matrix.decode(errored)
    assert message == [1, 1, 0, 0]
    assert corrected == codeword


def test_matrix_arithmetic_respects_binary_field():
    matrix = Hamming74Matrix()
    ones = np.ones_like(matrix.generator_matrix)
    complemented = matrix + 1
    np.testing.assert_array_equal(
        np.mod(matrix.generator_matrix + ones, 2), complemented.generator_matrix
    )

    product = matrix @ matrix.transpose()
    assert product.shape == (4, 4)


def test_nearest_codeword_requires_seven_bits():
    matrix = Hamming74Matrix()
    with pytest.raises(ValueError):
        matrix.nearest_codeword([1, 0, 1])
