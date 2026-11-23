from __future__ import annotations

import gzip
from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType


@ComponentBase.register_type(SimilarityBase, "GzipSimilarity")
class GzipSimilarity(SimilarityBase):
    """Gzip-based similarity using Normalized Compression Distance."""

    type: Literal["GzipSimilarity"] = "GzipSimilarity"
    compresslevel: int = Field(default=9, ge=0, le=9)
    symmetric: bool = True

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """Return a bounded similarity score between two values."""
        if self._to_bytes(x) == self._to_bytes(y):
            return 1.0

        ncd = self.ncd(x, y)
        return max(0.0, min(1.0, 1.0 - ncd))

    def ncd(self, x: ComparableType, y: ComparableType) -> float:
        """Return the underlying Normalized Compression Distance."""
        x_bytes = self._to_bytes(x)
        y_bytes = self._to_bytes(y)

        if x_bytes == y_bytes:
            return 0.0

        x_size = self.compressed_size(x_bytes)
        y_size = self.compressed_size(y_bytes)
        forward_size = self.compressed_size(x_bytes + y_bytes)

        if self.symmetric:
            reverse_size = self.compressed_size(y_bytes + x_bytes)
            joined_size = min(forward_size, reverse_size)
        else:
            joined_size = forward_size

        denominator = max(x_size, y_size)
        if denominator == 0:
            return 0.0 if x_bytes == y_bytes else 1.0

        return (joined_size - min(x_size, y_size)) / denominator

    def compressed_size(self, value: ComparableType) -> int:
        """Return the deterministic gzip-compressed size of a value."""
        return len(
            gzip.compress(
                self._to_bytes(value),
                compresslevel=self.compresslevel,
                mtime=0,
            )
        )

    def check_bounded(self) -> bool:
        """Return whether this similarity measure is bounded."""
        return True

    @staticmethod
    def _to_bytes(value: ComparableType) -> bytes:
        if isinstance(value, str):
            return value.encode("utf-8")
        if isinstance(value, bytes):
            return value
        if isinstance(value, bytearray):
            return bytes(value)
        if isinstance(value, memoryview):
            return value.tobytes()
        raise TypeError(
            "GzipSimilarity supports str, bytes, bytearray, and memoryview"
        )


# Expose the registered type name at both class and instance level.
GzipSimilarity.type = "GzipSimilarity"
