from tigrbl.runtime import events as _ev


def test_phases_constant_lists_all_phases_in_order() -> None:
    """Ensure PHASES exports the complete ordered phase sequence."""
    assert _ev.PHASES == (
        "PRE_TX",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "END_TX",
        "POST_RESPONSE",
    )
