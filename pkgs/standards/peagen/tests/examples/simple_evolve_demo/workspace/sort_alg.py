from __future__ import annotations


def bad_sort(values: list[int]) -> list[int]:
    """Return a sorted copy of *values* using an intentionally slow algorithm."""
    items = values[:]
    for _ in range(len(items)):
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[j] < items[i]:
                    items[i], items[j] = items[j], items[i]
    return items
