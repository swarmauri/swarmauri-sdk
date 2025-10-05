"""Hamming (7, 4) generator matrix packaged as a Swarmauri component."""

from __future__ import annotations

import itertools
import logging
from typing import Iterator, List, Literal, Sequence, Tuple, Union

import numpy as np

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.matrices.MatrixBase import MatrixBase
from swarmauri_metric_hamming import HammingMetric

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MatrixBase, "Hamming74Matrix")
class Hamming74Matrix(MatrixBase):
    """Concrete generator matrix for the binary ``(7, 4)`` Hamming code."""

    type: Literal["Hamming74Matrix"] = "Hamming74Matrix"

    _DEFAULT_GENERATOR = np.array(
        [
            [1, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1],
        ],
        dtype=int,
    )

    _DEFAULT_PARITY_CHECK = np.array(
        [
            [1, 1, 0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 0, 1],
        ],
        dtype=int,
    )

    def __init__(self, data: Sequence[Sequence[int]] | None = None) -> None:
        matrix = (
            np.array(data, dtype=int)
            if data is not None
            else self._DEFAULT_GENERATOR.copy()
        )
        self._matrix = self._validate_matrix(matrix)
        self._metric = HammingMetric()

    # ------------------------------------------------------------------
    # MatrixBase interface
    # ------------------------------------------------------------------
    def __getitem__(self, key: Union[int, slice, Tuple[Union[int, slice], ...]]):
        value = self._matrix[key]
        if isinstance(value, np.ndarray):
            return value.tolist()
        return int(value)

    def __setitem__(self, key, value) -> None:  # type: ignore[override]
        updated = self._matrix.copy()
        updated[key] = value
        self._matrix = self._validate_matrix(updated)

    @property
    def shape(self) -> Tuple[int, int]:
        return tuple(self._matrix.shape)  # type: ignore[return-value]

    def reshape(self, shape: Tuple[int, int]) -> "Hamming74Matrix":
        if shape != self._matrix.shape:
            raise ValueError("Hamming74Matrix is fixed at shape (4, 7)")
        return Hamming74Matrix(self.tolist())

    @property
    def dtype(self) -> type:
        return int

    def tolist(self) -> List[List[int]]:
        return self._matrix.astype(int).tolist()

    def row(self, index: int) -> List[int]:
        return self._matrix[index, :].astype(int).tolist()

    def column(self, index: int) -> List[int]:
        return self._matrix[:, index].astype(int).tolist()

    def __add__(
        self, other: Union["Hamming74Matrix", Sequence[Sequence[int]], int]
    ) -> "Hamming74Matrix":
        other_matrix = self._coerce_other(other)
        result = (self._matrix + other_matrix) % 2
        return Hamming74Matrix(result.tolist())

    def __sub__(
        self, other: Union["Hamming74Matrix", Sequence[Sequence[int]], int]
    ) -> "Hamming74Matrix":
        other_matrix = self._coerce_other(other)
        result = (self._matrix - other_matrix) % 2
        return Hamming74Matrix(result.tolist())

    def __mul__(
        self, other: Union["Hamming74Matrix", Sequence[Sequence[int]], int]
    ) -> "Hamming74Matrix":
        other_matrix = self._coerce_other(other)
        result = (self._matrix * other_matrix) % 2
        return Hamming74Matrix(result.tolist())

    def __matmul__(self, other: Union[Sequence[int], Sequence[Sequence[int]]]):
        other_array = np.array(other, dtype=int)
        if other_array.ndim == 1:
            if other_array.shape[0] != self._matrix.shape[1]:
                raise ValueError("Vector length must match matrix columns (7)")
            result = self._matrix.dot(other_array) % 2
            return result.astype(int).tolist()
        if other_array.ndim == 2:
            if other_array.shape[0] != self._matrix.shape[1]:
                raise ValueError("Matrix row count must match matrix columns (7)")
            result = (self._matrix @ other_array) % 2
            return result.astype(int).tolist()
        raise TypeError("Unsupported operand for matrix multiplication")

    def __truediv__(self, other: int) -> "Hamming74Matrix":
        if other != 1:
            raise NotImplementedError("Hamming74Matrix only supports division by 1")
        return Hamming74Matrix(self.tolist())

    def __neg__(self) -> "Hamming74Matrix":
        return Hamming74Matrix(((-self._matrix) % 2).astype(int).tolist())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hamming74Matrix):
            return False
        return bool(np.array_equal(self._matrix, other._matrix))

    def __iter__(self) -> Iterator[List[int]]:
        for row in self._matrix:
            yield row.astype(int).tolist()

    def transpose(self):  # type: ignore[override]
        raise NotImplementedError(
            "Transpose is not defined for the fixed Hamming74Matrix shape"
        )

    def __array__(self) -> np.ndarray:  # type: ignore[override]
        return self._matrix.copy()

    # ------------------------------------------------------------------
    # Hamming-code specific helpers
    # ------------------------------------------------------------------
    @property
    def parity_check_matrix(self) -> List[List[int]]:
        return self._DEFAULT_PARITY_CHECK.astype(int).tolist()

    def encode(self, message: Sequence[int]) -> List[int]:
        if len(message) != 4:
            raise ValueError("Message length must be 4 for Hamming(7,4)")
        message_array = np.array(message, dtype=int)
        if not self._is_binary(message_array):
            raise ValueError("Message symbols must be binary (0 or 1)")
        codeword = message_array.dot(self._matrix) % 2
        return codeword.astype(int).tolist()

    def syndrome(self, codeword: Sequence[int]) -> List[int]:
        code_array = np.array(codeword, dtype=int)
        if code_array.shape != (7,):
            raise ValueError("Codeword must contain exactly 7 bits")
        if not self._is_binary(code_array):
            raise ValueError("Codeword symbols must be binary (0 or 1)")
        syndrome = self._DEFAULT_PARITY_CHECK.dot(code_array) % 2
        return syndrome.astype(int).tolist()

    def correct(self, received: Sequence[int]) -> List[int]:
        code_array = np.array(received, dtype=int)
        if code_array.shape != (7,):
            raise ValueError("Received vector must contain exactly 7 bits")
        if not self._is_binary(code_array):
            raise ValueError("Received vector must be binary (0 or 1)")
        syndrome = self.syndrome(code_array)
        if not any(syndrome):
            return code_array.astype(int).tolist()
        syndrome_vector = np.array(syndrome, dtype=int)
        for index in range(self._matrix.shape[1]):
            column = self._DEFAULT_PARITY_CHECK[:, index]
            if np.array_equal(column, syndrome_vector):
                code_array[index] ^= 1
                logger.debug("Corrected error at position %s", index)
                return code_array.astype(int).tolist()
        logger.debug("Syndrome %s did not match a single-bit error", syndrome)
        return code_array.astype(int).tolist()

    def distance(self, a: Sequence[int], b: Sequence[int]) -> float:
        return self._metric.distance(a, b)

    def minimum_distance(self) -> int:
        codewords = self._all_codewords()
        min_distance = min(
            self._metric.distance(x, y)
            for i, x in enumerate(codewords)
            for y in codewords[i + 1 :]
            if x != y
        )
        return int(min_distance)

    def nearest_codeword(self, received: Sequence[int]) -> List[int]:
        received_array = np.array(received, dtype=int)
        if received_array.shape != (7,):
            raise ValueError("Received vector must contain exactly 7 bits")
        if not self._is_binary(received_array):
            raise ValueError("Received vector must be binary (0 or 1)")
        best_codeword: List[int] | None = None
        best_distance: float | None = None
        for codeword in self._all_codewords():
            distance = self._metric.distance(received_array.tolist(), codeword)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_codeword = codeword
        return (
            best_codeword
            if best_codeword is not None
            else received_array.astype(int).tolist()
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _validate_matrix(self, matrix: np.ndarray) -> np.ndarray:
        if matrix.shape != (4, 7):
            raise ValueError("Hamming74Matrix must be 4x7")
        if not self._is_binary(matrix):
            raise ValueError("Matrix entries must be binary (0 or 1)")
        return matrix.astype(int)

    def _coerce_other(
        self, other: Union["Hamming74Matrix", Sequence[Sequence[int]], int]
    ) -> np.ndarray:
        if isinstance(other, Hamming74Matrix):
            return other._matrix
        if isinstance(other, Sequence) and not isinstance(other, (str, bytes)):
            arr = np.array(other, dtype=int)
            if arr.shape != self._matrix.shape:
                raise ValueError("Operand must match matrix shape (4, 7)")
            if not self._is_binary(arr):
                raise ValueError("Operand entries must be binary (0 or 1)")
            return arr
        if isinstance(other, int):
            if other not in (0, 1):
                raise ValueError("Scalar operands must be binary (0 or 1)")
            return np.full(self._matrix.shape, other, dtype=int)
        raise TypeError("Unsupported operand type")

    def _is_binary(self, array: np.ndarray) -> bool:
        return np.isin(array, [0, 1]).all()

    def _all_codewords(self) -> List[List[int]]:
        codewords: List[List[int]] = []
        for message in itertools.product([0, 1], repeat=4):
            codewords.append(self.encode(message))
        return codewords
