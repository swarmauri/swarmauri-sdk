import httpx
import pytest

from peagen.transport import (
    Response,
    parse_request,
    _registry,
    KEYS_UPLOAD,
    SECRETS_ADD,
)
from peagen.cli.task_helpers import build_task, submit_task


def test_parse_and_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_post(url: str, json: dict, timeout: float) -> object:
        captured["json"] = json

        class Resp:
            def raise_for_status(self) -> None:
                pass

            def json(self) -> dict:
                return {"ok": True}

        return Resp()

    monkeypatch.setattr(httpx, "post", fake_post)

    task = build_task("demo", {}, pool="default")
    submit_task("http://gw/rpc", task)

    raw = captured["json"]
    assert isinstance(raw, dict)
    req = parse_request(raw)
    PModel = _registry.params_model(req.method)
    params = PModel.model_validate(req.params)
    assert params.pool == "default"
    res = Response.ok(id=req.id, result={"taskId": "ABCDEFGHIJKL"})
    assert res.jsonrpc == "2.0"


def test_keys_upload() -> None:
    raw = {
        "jsonrpc": "2.0",
        "id": "k",
        "method": KEYS_UPLOAD,
        "params": {"public_key": "PUB"},
    }
    req = parse_request(raw)
    PModel = _registry.params_model(req.method)
    params = PModel.model_validate(req.params)
    assert params.public_key == "PUB"


def test_secrets_add() -> None:
    raw = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": SECRETS_ADD,
        "params": {"name": "s", "cipher": "c"},
    }
    req = parse_request(raw)
    PModel = _registry.params_model(req.method)
    params = PModel.model_validate(req.params)
    assert params.name == "s"
