import json
import pytest

import peagen.gateway as gw


@pytest.mark.unit
def test_pick_worker_handles_handlers():
    workers = [
        {"url": "http://w1", "handlers": json.dumps(["a", "b"])},
        {"url": "http://w2", "handlers": json.dumps(["c"])},
    ]

    assert gw._pick_worker(workers, "c")["url"] == "http://w2"
    assert gw._pick_worker(workers, "x") is None
