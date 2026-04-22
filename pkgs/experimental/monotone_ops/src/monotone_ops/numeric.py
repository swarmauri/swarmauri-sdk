"""Numeric monotone operators under the usual order."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

Number = int | float


def num_leq(a: Number, b: Number) -> bool:
    return a <= b


def num_max(a: Number, b: Number) -> Number:
    """Join for the usual numeric order."""

    return a if a >= b else b


def num_min(a: Number, b: Number) -> Number:
    """Meet for the usual numeric order."""

    return a if a <= b else b


def add_nonnegative(a: Number, b: Number) -> Number:
    """Addition restricted to non-negative evidence values."""

    if a < 0 or b < 0:
        raise ValueError("add_nonnegative expects non-negative operands")
    return a + b


def mul_nonnegative(a: Number, b: Number) -> Number:
    """Multiplication restricted to non-negative values."""

    if a < 0 or b < 0:
        raise ValueError("mul_nonnegative expects non-negative operands")
    return a * b


@dataclass(frozen=True, slots=True)
class Bounds:
    lo: float | None = None
    hi: float | None = None

    def clamp(self, x: Number) -> float:
        y = float(x)
        if self.lo is not None and y < self.lo:
            y = self.lo
        if self.hi is not None and y > self.hi:
            y = self.hi
        return y


def clamp(bounds: Bounds) -> Callable[[Number], float]:
    return bounds.clamp


def capped_max(bounds: Bounds) -> Callable[[Number, Number], float]:
    """Clamp operands, then take max."""

    def merge(a: Number, b: Number) -> float:
        return max(bounds.clamp(a), bounds.clamp(b))

    return merge


def capped_min(bounds: Bounds) -> Callable[[Number, Number], float]:
    """Clamp operands, then take min."""

    def merge(a: Number, b: Number) -> float:
        return min(bounds.clamp(a), bounds.clamp(b))

    return merge


def saturating_sum(cap: Number) -> Callable[[Number, Number], Number]:
    """Non-negative sum capped at ``cap``.

    Mathematically associative on non-negative values: min(cap, a + b).
    """

    if cap < 0:
        raise ValueError("cap must be non-negative")

    def merge(a: Number, b: Number) -> Number:
        if a < 0 or b < 0:
            raise ValueError("saturating_sum expects non-negative operands")
        return min(cap, a + b)

    return merge


def saturating_product(cap: Number) -> Callable[[Number, Number], Number]:
    """Non-negative product capped at ``cap``."""

    if cap < 0:
        raise ValueError("cap must be non-negative")

    def merge(a: Number, b: Number) -> Number:
        if a < 0 or b < 0:
            raise ValueError("saturating_product expects non-negative operands")
        return min(cap, a * b)

    return merge


def affine_increasing(scale: Number, bias: Number = 0) -> Callable[[Number], float]:
    """Increasing affine map ``scale*x + bias`` for ``scale >= 0``."""

    if scale < 0:
        raise ValueError("scale must be non-negative")

    def fn(x: Number) -> float:
        return float(scale * x + bias)

    return fn


def positive_linear(weights: Sequence[Number], bias: Number = 0) -> Callable[[Sequence[Number]], float]:
    """Monotone linear form with non-negative coefficients."""

    if any(weight < 0 for weight in weights):
        raise ValueError("all weights must be non-negative")
    frozen = tuple(float(weight) for weight in weights)

    def fn(xs: Sequence[Number]) -> float:
        if len(xs) != len(frozen):
            raise ValueError("input length does not match weights")
        return float(bias) + sum(weight * float(x) for weight, x in zip(frozen, xs, strict=True))

    return fn


def floor_quantize(step: Number) -> Callable[[Number], float]:
    """Monotone quantizer ``floor(x / step) * step`` for ``step > 0``."""

    if step <= 0:
        raise ValueError("step must be positive")

    def fn(x: Number) -> float:
        return math.floor(float(x) / float(step)) * float(step)

    return fn


def ceil_quantize(step: Number) -> Callable[[Number], float]:
    """Monotone quantizer ``ceil(x / step) * step`` for ``step > 0``."""

    if step <= 0:
        raise ValueError("step must be positive")

    def fn(x: Number) -> float:
        return math.ceil(float(x) / float(step)) * float(step)

    return fn


def power_increasing(exponent: Number) -> Callable[[Number], float]:
    """Increasing power map on non-negative inputs for ``exponent >= 0``."""

    if exponent < 0:
        raise ValueError("exponent must be non-negative")

    def fn(x: Number) -> float:
        if x < 0:
            raise ValueError("power_increasing expects non-negative inputs")
        return float(float(x) ** float(exponent))

    return fn


def soft_cap(cap: Number, sharpness: float = 1.0) -> Callable[[Number], float]:
    """Smooth increasing cap approaching ``cap`` for non-negative inputs."""

    if cap <= 0 or sharpness <= 0:
        raise ValueError("cap and sharpness must be positive")

    def fn(x: Number) -> float:
        if x < 0:
            raise ValueError("soft_cap expects non-negative inputs")
        return float(cap) * (1.0 - math.exp(-sharpness * float(x) / float(cap)))

    return fn
