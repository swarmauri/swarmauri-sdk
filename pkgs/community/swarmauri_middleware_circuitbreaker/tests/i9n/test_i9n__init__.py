"""
Tests for the package initializer of swarmauri_middleware_circuitbreaker.
"""

import pytest
import logging
from swarmauri_middleware_circuitbreaker import (
    CircuitBreakerMiddleware,
    __version__,
)

logger = logging.getLogger(__name__)


@pytest.mark.i9n
def test_package_initializer() -> None:
    """
    Test that the package initializer loads correctly and exports the expected classes.
    """
    logger.info("Testing package initializer")

    # Test CircuitBreakerMiddleware is imported correctly
    assert CircuitBreakerMiddleware, "CircuitBreakerMiddleware is not imported"
    assert isinstance(CircuitBreakerMiddleware, type), (
        "CircuitBreakerMiddleware is not a class"
    )


@pytest.mark.i9n
def test_version() -> None:
    """
    Test that the package version is correctly set.
    """
    logger.info("Testing package version")

    # Test version is a string
    assert isinstance(__version__, str), "__version__ is not a string"
    assert len(__version__) > 0, "__version__ is empty"
