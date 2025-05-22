# File: tests/workflows/input_modes/test_base_input_mode.py

import pytest
from swarmauri_workflow_statedriven.input_modes.base import InputMode


@pytest.mark.unit
def test_input_mode_is_abstract():
    """
    File: workflows/input_modes/base.py
    Class: InputMode
    Method: prepare (abstract)

    Ensure that InputMode cannot be instantiated directly.
    """
    with pytest.raises(TypeError):
        InputMode()


class DummyMode(InputMode):
    """
    Concrete subclass implementing prepare for testing.
    """

    def prepare(self, state_manager, node_name, data, results):
        return f"prepared:{data}"


@pytest.mark.unit
def test_dummy_mode_prepare_returns_expected():
    """
    File: workflows/input_modes/base.py
    Class: DummyMode (subclass of InputMode)
    Method: prepare

    Ensure that a concrete subclass’s prepare is invoked correctly.
    """
    mode = DummyMode()
    # state_manager and results can be None or empty dict for this test
    out = mode.prepare(state_manager=None, node_name="X", data="input", results={})
    assert out == "prepared:input"
