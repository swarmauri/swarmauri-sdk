from swarmauri_agent_realtime import LiveSessionPool


def test_pool_starts_empty():
    assert LiveSessionPool().get("missing") is None
