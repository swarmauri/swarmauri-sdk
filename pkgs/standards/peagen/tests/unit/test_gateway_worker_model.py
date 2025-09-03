from peagen.gateway import app


def test_worker_model_registered() -> None:
    assert "Worker" in app.models, "Worker model should be registered in the gateway"
