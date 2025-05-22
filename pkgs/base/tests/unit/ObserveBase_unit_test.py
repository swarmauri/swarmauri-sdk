import pytest
from swarmauri_base.ObserveBase import ObserveBase
from swarmauri_base.DynamicBase import DynamicBase

@DynamicBase.register_type()
class CustomObserver(ObserveBase):
    pass

@pytest.mark.unit
def test_observe_base_registration_and_defaults():
    obs = CustomObserver()
    assert obs.type == "CustomObserver"
    reg = DynamicBase._registry["ObserveBase"]["subtypes"]
    assert reg["CustomObserver"] is CustomObserver
