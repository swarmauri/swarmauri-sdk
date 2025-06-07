"""Example bad sort implementation."""

def sort(arr):
    """Return a sorted list in ascending order using a naive algorithm."""
    arr = list(arr)
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
    return arr
