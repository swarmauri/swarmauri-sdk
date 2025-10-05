"""MatrixBase implementation for the binary Hamming (7,4) code."""

from __future__ import annotations

from itertools import product
from typing import Iterator, List, Literal, Optional, Sequence, Tuple, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.matrices.MatrixBase import MatrixBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput

from swarmauri_metric_hamming import HammingMetric

BinaryLike = Union[
    "Hamming74Matrix",
    IMatrix,
    Sequence[Sequence[int]],
    Sequence[int],
    np.ndarray,
    int,
]

_DEFAULT_MATRIX = np.array(
    [
        [1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 1],
        [0, 0, 1, 0, 0, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
    ],
    dtype=int,
)

_PARITY_CHECK = np.array(
    [
        [1, 1, 0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 1],
    ],
    dtype=int,
)


@ComponentBase.register_type(MatrixBase, "Hamming74Matrix")
class Hamming74Matrix(MatrixBase):
    """Concrete matrix that models the Hamming (7,4) linear block code."""

    type: Literal["Hamming74Matrix"] = "Hamming74Matrix"

    def __init__(self, data: Optional[Sequence[Sequence[int]]] = None) -> None:
        source = _DEFAULT_MATRIX if data is None else np.array(data, dtype=int)
        if source.ndim != 2:
            raise ValueError("Hamming74Matrix requires a 2D array of integers")
        self._data = np.mod(source, 2)
        self._metric = HammingMetric()

    # ------------------------------------------------------------------
    # MatrixBase protocol implementation
    # ------------------------------------------------------------------
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = np.mod(value, 2)

    @property
    def shape(self) -> Tuple[int, int]:
        return tuple(self._data.shape)

    def reshape(self, shape: Tuple[int, int]) -> "Hamming74Matrix":
        return Hamming74Matrix(self._data.reshape(shape))

    @property
    def dtype(self) -> type:
        return self._data.dtype.type

    def tolist(self) -> List[List[int]]:
        return self._data.tolist()

    def row(self, index: int) -> np.ndarray:
        return self._data[index, :].copy()

    def column(self, index: int) -> np.ndarray:
        return self._data[:, index].copy()

    def _coerce(self, other: BinaryLike) -> np.ndarray:
        if isinstance(other, Hamming74Matrix):
            return other._data
        if isinstance(other, np.ndarray):
            return np.mod(other, 2)
        if isinstance(other, IMatrix):
            return np.mod(np.array(other.tolist(), dtype=int), 2)
        if isinstance(other, Sequence):
            return np.mod(np.array(other, dtype=int), 2)
        if isinstance(other, int):
            return np.mod(np.full(self.shape, other, dtype=int), 2)
        raise TypeError(f"Unsupported operand type: {type(other)!r}")

    def __add__(self, other: BinaryLike) -> "Hamming74Matrix":
        return Hamming74Matrix((self._data + self._coerce(other)) % 2)

    def __sub__(self, other: BinaryLike) -> "Hamming74Matrix":
        return Hamming74Matrix((self._data - self._coerce(other)) % 2)

    def __mul__(self, other: BinaryLike) -> "Hamming74Matrix":
        return Hamming74Matrix((self._data * self._coerce(other)) % 2)

    def __matmul__(self, other: Union[BinaryLike, np.ndarray]) -> "Hamming74Matrix":
        matrix = self._coerce(other)
        if self.shape[1] != matrix.shape[0]:
            raise ValueError("Matrix dimensions do not align for multiplication")
        return Hamming74Matrix(np.mod(self._data @ matrix, 2))

    def __truediv__(self, other: BinaryLike) -> "Hamming74Matrix":
        raise NotImplementedError("Division is undefined in GF(2)")

    def __neg__(self) -> "Hamming74Matrix":
        return Hamming74Matrix(self._data.copy())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Hamming74Matrix, np.ndarray, Sequence)):
            return False
        return np.array_equal(self._data, self._coerce(other))

    def __iter__(self) -> Iterator[np.ndarray]:
        for row in self._data:
            yield row.copy()

    def transpose(self) -> "Hamming74Matrix":
        return Hamming74Matrix(self._data.T)

    def __array__(self) -> np.ndarray:  # pragma: no cover - numpy protocol helper
        return np.array(self._data, copy=True)

    # ------------------------------------------------------------------
    # Hamming code helpers
    # ------------------------------------------------------------------
    @property
    def generator_matrix(self) -> np.ndarray:
        """Return the 4x7 generator matrix G."""

        return self._data.copy()

    @property
    def parity_check_matrix(self) -> np.ndarray:
        """Return the 3x7 parity-check matrix H."""

        return _PARITY_CHECK.copy()

    def encode(self, message: Sequence[int]) -> List[int]:
        bits = np.mod(np.array(message, dtype=int), 2)
        if bits.size != 4:
            raise ValueError("Hamming (7,4) encoding expects exactly 4 message bits")
        codeword = np.mod(bits @ self._data, 2)
        return codeword.astype(int).tolist()

    def syndrome(self, word: Sequence[int]) -> List[int]:
        bits = np.mod(np.array(word, dtype=int), 2)
        if bits.size != 7:
            raise ValueError("Syndrome calculation expects a 7-bit codeword")
        result = np.mod(self.parity_check_matrix @ bits, 2)
        return result.astype(int).tolist()

    def codewords(self) -> List[List[int]]:
        return [self.encode(message) for message in product([0, 1], repeat=4)]

    def _normalise_vector(self, word: MetricInput) -> np.ndarray:
        normalised = np.array(self._metric.normalise(word), dtype=int)
        return np.mod(normalised, 2)

    def nearest_codeword(self, word: MetricInput) -> List[int]:
        candidate = self._normalise_vector(word)
        if candidate.size != 7:
            raise ValueError("Nearest codeword search expects 7-bit inputs")
        codebook = self.codewords()
        distances = [
            self._metric.distance(candidate.tolist(), codeword) for codeword in codebook
        ]
        index = int(np.argmin(distances))
        return codebook[index]

    def decode(self, word: MetricInput) -> Tuple[List[int], List[int]]:
        """Decode a noisy 7-bit sequence into ``(message, codeword)``."""

        nearest = self.nearest_codeword(word)
        message = nearest[:4]
        return message, nearest


__all__ = ["Hamming74Matrix"]
