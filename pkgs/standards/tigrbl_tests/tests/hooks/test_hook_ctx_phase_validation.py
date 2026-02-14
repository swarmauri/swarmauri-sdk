from enum import Enum

import pytest

from tigrbl.hook import InvalidHookPhaseError, hook_ctx
from tigrbl.hook.types import PHASE


class InvalidPhase(Enum):
    IN_BUILD = "IN_BUILD"


def test_hook_ctx_valid_string_phase_does_not_raise():
    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def valid_string_hook(cls, ctx):
        return None

    assert valid_string_hook is not None


def test_hook_ctx_invalid_string_phase_raises_immediately():
    with pytest.raises(InvalidHookPhaseError) as exc_info:

        @hook_ctx(ops="create", phase="IN_BUILD")
        def invalid_string_hook(cls, ctx):
            return None

    message = str(exc_info.value)
    assert "Invalid hook phase 'IN_BUILD'." in message
    assert "Valid phases are:" in message
    assert "PRE_HANDLER" in message
    assert "ON_ROLLBACK" in message


def test_hook_ctx_valid_enum_phase_does_not_raise():
    @hook_ctx(ops="create", phase=PHASE.PRE_HANDLER)
    def valid_enum_hook(cls, ctx):
        return None

    assert valid_enum_hook is not None


def test_hook_ctx_invalid_enum_phase_raises_immediately():
    with pytest.raises(InvalidHookPhaseError) as exc_info:

        @hook_ctx(ops="create", phase=InvalidPhase.IN_BUILD)
        def invalid_enum_hook(cls, ctx):
            return None

    message = str(exc_info.value)
    assert "Invalid hook phase 'IN_BUILD'." in message
    assert "Valid phases are:" in message
    assert "PRE_HANDLER" in message
    assert "ON_ROLLBACK" in message
