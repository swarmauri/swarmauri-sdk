from tigrbl.runtime import events as _ev


def test_phases_constant_lists_all_phases_in_order() -> None:
    """Ensure PHASES exports the complete ordered phase sequence."""
    assert _ev.PHASES == (
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "END_TX",
        "POST_COMMIT",
        "POST_RESPONSE",
        "ON_ERROR",
        "ON_PRE_TX_BEGIN_ERROR",
        "ON_START_TX_ERROR",
        "ON_PRE_HANDLER_ERROR",
        "ON_HANDLER_ERROR",
        "ON_POST_HANDLER_ERROR",
        "ON_PRE_COMMIT_ERROR",
        "ON_END_TX_ERROR",
        "ON_POST_COMMIT_ERROR",
        "ON_POST_RESPONSE_ERROR",
        "ON_ROLLBACK",
    )
