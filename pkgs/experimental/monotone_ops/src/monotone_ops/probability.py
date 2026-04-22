"""Monotone probability, confidence, and evidence-score operators."""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Mapping

K = Hashable


def _prob(x: float) -> float:
    if not 0.0 <= x <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    return float(x)


def confidence_max(a: float, b: float) -> float:
    return max(_prob(a), _prob(b))


def confidence_min(a: float, b: float) -> float:
    return min(_prob(a), _prob(b))


def noisy_or(a: float, b: float) -> float:
    """Independent-evidence OR: ``1 - (1-a)(1-b)``."""

    a, b = _prob(a), _prob(b)
    return 1.0 - (1.0 - a) * (1.0 - b)


def prob_and(a: float, b: float) -> float:
    """Independent-evidence AND/product. Monotone on [0, 1]."""

    return _prob(a) * _prob(b)


def odds_product(a: float, b: float, *, cap: float = math.inf) -> float:
    """Multiply non-negative odds/evidence ratios with optional cap."""

    if a < 0 or b < 0 or cap < 0:
        raise ValueError("odds and cap must be non-negative")
    return min(cap, a * b)


def logaddexp(a: float, b: float) -> float:
    """Stable log(exp(a)+exp(b)); monotone in each argument."""

    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))


def log_evidence_sum(a: float, b: float) -> float:
    return logaddexp(a, b)


def bounded_evidence_sum(cap: float) -> Callable[[float, float], float]:
    if cap < 0:
        raise ValueError("cap must be non-negative")

    def merge(a: float, b: float) -> float:
        if a < 0 or b < 0:
            raise ValueError("evidence must be non-negative")
        return min(cap, a + b)

    return merge


def pointwise_cdf_min(a: Mapping[float, float], b: Mapping[float, float]) -> dict[float, float]:
    """Pointwise lower envelope for CDF samples."""

    keys = a.keys() | b.keys()
    return {key: min(_prob(a.get(key, 1.0)), _prob(b.get(key, 1.0))) for key in keys}


def pointwise_cdf_max(a: Mapping[float, float], b: Mapping[float, float]) -> dict[float, float]:
    """Pointwise upper envelope for CDF samples."""

    keys = a.keys() | b.keys()
    return {key: max(_prob(a.get(key, 0.0)), _prob(b.get(key, 0.0))) for key in keys}


def normalize_weights(weights: Mapping[K, float]) -> dict[K, float]:
    total = sum(weights.values())
    if total < 0 or any(v < 0 for v in weights.values()):
        raise ValueError("weights must be non-negative")
    if total == 0:
        return {key: 0.0 for key in weights}
    return {key: value / total for key, value in weights.items()}
