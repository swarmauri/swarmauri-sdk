import pytest

from tigrbl.hook import InvalidHookPhaseError, hook_ctx


def test_hook_ctx_invalid_phase_raises_immediately():
    with pytest.raises(InvalidHookPhaseError) as exc_info:

        @hook_ctx(ops="create", phase="IN_BUILD")
        def invalid_hook(cls, ctx):
            return None

    message = str(exc_info.value)
    assert "Invalid hook phase 'IN_BUILD'." in message
    assert "Valid phases are:" in message
    assert "PRE_HANDLER" in message
    assert "ON_ROLLBACK" in message


def test_hook_ctx_valid_phase_does_not_raise():
    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def valid_hook(cls, ctx):
        return None

    assert valid_hook is not None
