from __future__ import annotations


def greet(name: str) -> str:
    """Return a greeting for the provided name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(greet("World"))
