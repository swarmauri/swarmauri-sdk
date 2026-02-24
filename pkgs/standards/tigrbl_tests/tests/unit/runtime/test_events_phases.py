from tigrbl.hook.types import PHASES as HOOK_PHASES
from tigrbl.runtime import events as _ev


def test_phases_constant_lists_all_phases_in_order() -> None:
    """Ensure runtime PHASES exports the complete ingress→egress ordered sequence."""
    assert _ev.PHASES == (
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_ROUTE",
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "END_TX",
        "POST_COMMIT",
        "EGRESS_SHAPE",
        "EGRESS_FINALIZE",
        "POST_RESPONSE",
    )


def test_hook_phases_include_all_error_phases_in_lifecycle_order() -> None:
    error_phases = (
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

    for phase in error_phases:
        assert phase in HOOK_PHASES

    base_order = HOOK_PHASES[:9]
    assert base_order == (
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "END_TX",
        "POST_COMMIT",
        "POST_RESPONSE",
    )
    assert HOOK_PHASES[9:] == error_phases
