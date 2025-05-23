"""Unit tests for ``ObserveBase`` registration mechanics."""

import pytest
from swarmauri_base.ObserveBase import ObserveBase
from swarmauri_base.DynamicBase import DynamicBase


@DynamicBase.register_type()
class CustomObserver(ObserveBase):
    """Concrete observer used in tests."""


@pytest.mark.unit
def test_observe_base_registration_and_defaults():
    """Check registration and default values."""
    obs = CustomObserver()
    assert obs.type == "CustomObserver"
    reg = DynamicBase._registry["ObserveBase"]["subtypes"]
    assert reg["CustomObserver"] is CustomObserver
