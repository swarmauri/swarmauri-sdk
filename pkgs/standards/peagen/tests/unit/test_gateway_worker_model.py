from peagen.gateway import api


def test_worker_model_registered() -> None:
    assert "Worker" in api.models, "Worker model should be registered in the gateway"
