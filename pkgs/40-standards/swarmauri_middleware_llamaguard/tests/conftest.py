"""Test configuration for swarmauri_middleware_llamaguard."""

from __future__ import annotations

import os
from typing import Iterator

import pytest


@pytest.fixture(autouse=True, scope="session")
def clear_groq_api_key() -> Iterator[None]:
    """Ensure tests run without a real Groq API key."""

    original = os.environ.pop("GROQ_API_KEY", None)
    try:
        yield
    finally:
        if original is not None:
            os.environ["GROQ_API_KEY"] = original
