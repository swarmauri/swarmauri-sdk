from tigrbl.runtime import events as _ev


def test_order_events_returns_canonical_runtime_sequence() -> None:
    anchors = [_ev.OUT_DUMP, _ev.DEP_SECURITY, _ev.OUT_BUILD]

    assert _ev.order_events(anchors) == [_ev.DEP_SECURITY, _ev.OUT_BUILD, _ev.OUT_DUMP]


def test_prune_events_for_persist_keeps_non_persist_tied_only() -> None:
    anchors = [_ev.RESOLVE_VALUES, _ev.SCHEMA_COLLECT_IN, _ev.OUT_DUMP]

    assert _ev.prune_events_for_persist(anchors, persist=False) == [
        _ev.SCHEMA_COLLECT_IN,
        _ev.OUT_DUMP,
    ]


def test_phases_follow_expected_kernel_execution_order() -> None:
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
