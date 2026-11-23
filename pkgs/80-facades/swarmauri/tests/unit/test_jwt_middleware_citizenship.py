"""Tests for JWT middleware first-class citizenship."""

import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

pytestmark = pytest.mark.unit


def test_jwt_middleware_is_first_class() -> None:
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.middlewares.JWTMiddleware"
        ]
        == "swarmauri_middleware_jwt.JWTMiddleware"
    )
    assert (
        "swarmauri.middlewares.AuthMiddleware"
        not in PluginCitizenshipRegistry.total_registry()
    )
