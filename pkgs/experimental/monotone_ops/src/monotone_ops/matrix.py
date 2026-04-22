"""Entrywise matrix/grid monotone operators, including morphology filters."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
Number = int | float

Grid = Sequence[Sequence[T]]


def _shape(grid: Grid[T]) -> tuple[int, int]:
    if not grid:
        return (0, 0)
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("ragged grid")
    return (len(grid), width)


def entrywise(op: Callable[[T, T], T]) -> Callable[[Grid[T], Grid[T]], tuple[tuple[T, ...], ...]]:
    def merge(a: Grid[T], b: Grid[T]) -> tuple[tuple[T, ...], ...]:
        if _shape(a) != _shape(b):
            raise ValueError("grid shapes differ")
        return tuple(
            tuple(op(x, y) for x, y in zip(row_a, row_b, strict=True))
            for row_a, row_b in zip(a, b, strict=True)
        )

    return merge


def entrywise_max(a: Grid[Number], b: Grid[Number]) -> tuple[tuple[Number, ...], ...]:
    return entrywise(max)(a, b)


def entrywise_min(a: Grid[Number], b: Grid[Number]) -> tuple[tuple[Number, ...], ...]:
    return entrywise(min)(a, b)


def entrywise_add_nonnegative(a: Grid[Number], b: Grid[Number]) -> tuple[tuple[Number, ...], ...]:
    def add(x: Number, y: Number) -> Number:
        if x < 0 or y < 0:
            raise ValueError("non-negative grids required")
        return x + y

    return entrywise(add)(a, b)


def matrix_leq(leq: Callable[[T, T], bool]) -> Callable[[Grid[T], Grid[T]], bool]:
    def inner(a: Grid[T], b: Grid[T]) -> bool:
        if _shape(a) != _shape(b):
            return False
        return all(
            leq(x, y) for row_a, row_b in zip(a, b, strict=True) for x, y in zip(row_a, row_b, strict=True)
        )

    return inner


def transpose(grid: Grid[T]) -> tuple[tuple[T, ...], ...]:
    rows, cols = _shape(grid)
    return tuple(tuple(grid[i][j] for i in range(rows)) for j in range(cols))


def max_dilate(grid: Grid[Number], offsets: Sequence[tuple[int, int]]) -> tuple[tuple[Number, ...], ...]:
    """Grey-scale dilation over clipped shifted neighbors.

    Cells whose clipped neighborhood is empty keep their original value.
    """

    rows, cols = _shape(grid)
    if not offsets:
        raise ValueError("offsets must be non-empty")
    out: list[list[Number]] = []
    for r in range(rows):
        row: list[Number] = []
        for c in range(cols):
            vals = [grid[r + dr][c + dc] for dr, dc in offsets if 0 <= r + dr < rows and 0 <= c + dc < cols]
            row.append(max(vals) if vals else grid[r][c])
        out.append(row)
    return tuple(tuple(row) for row in out)


def min_erode(grid: Grid[Number], offsets: Sequence[tuple[int, int]]) -> tuple[tuple[Number, ...], ...]:
    """Grey-scale erosion over clipped shifted neighbors.

    Cells whose clipped neighborhood is empty keep their original value.
    """

    rows, cols = _shape(grid)
    if not offsets:
        raise ValueError("offsets must be non-empty")
    out: list[list[Number]] = []
    for r in range(rows):
        row: list[Number] = []
        for c in range(cols):
            vals = [grid[r + dr][c + dc] for dr, dc in offsets if 0 <= r + dr < rows and 0 <= c + dc < cols]
            row.append(min(vals) if vals else grid[r][c])
        out.append(row)
    return tuple(tuple(row) for row in out)


def four_neighborhood() -> tuple[tuple[int, int], ...]:
    return ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))


def eight_neighborhood() -> tuple[tuple[int, int], ...]:
    return tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1))
