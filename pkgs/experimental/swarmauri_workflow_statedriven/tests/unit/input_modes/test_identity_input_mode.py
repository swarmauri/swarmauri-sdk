# File: tests/workflows/input_modes/test_identity_input_mode.py

import pytest
from swarmauri_workflow_statedriven.input_modes.identity import IdentityInputMode


class DummyStateManager:
    """Stub state manager; not used by IdentityInputMode."""

    pass


@pytest.mark.unit
def test_prepare_pass_through_scalar():
    """
    File: workflows/input_modes/identity.py
    Class: IdentityInputMode
    Method: prepare

    Should return scalar values unchanged.
    """
    mode = IdentityInputMode()
    sm = DummyStateManager()
    results = {"foo": "bar"}
    for scalar in [42, "foo", {"k": "v"}]:
        out = mode.prepare(
            state_manager=sm, node_name="N", data=scalar, results=results
        )
        assert out == scalar


@pytest.mark.unit
def test_prepare_pass_through_list_identity():
    """
    File: workflows/input_modes/identity.py
    Class: IdentityInputMode
    Method: prepare

    Should return the same list instance unchanged.
    """
    mode = IdentityInputMode()
    sm = DummyStateManager()
    lst = [1, 2, 3]
    out = mode.prepare(state_manager=sm, node_name="N", data=lst, results={})
    assert out is lst


@pytest.mark.unit
def test_prepare_pass_through_none():
    """
    File: workflows/input_modes/identity.py
    Class: IdentityInputMode
    Method: prepare

    Should return None unchanged.
    """
    mode = IdentityInputMode()
    sm = DummyStateManager()
    out = mode.prepare(state_manager=sm, node_name="N", data=None, results={})
    assert out is None
