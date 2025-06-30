from peagen.transport import (
    Response,
    parse_request,
    _registry,
    TASK_SUBMIT,
    KEYS_UPLOAD,
    SECRETS_ADD,
)


def test_parse_and_registry() -> None:
    raw = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": TASK_SUBMIT,
        "params": {
            "id": "11111111-2222-3333-4444-555555555555",
            "pool": "default",
            "payload": {"action": "demo"},
            "status": "queued",
            "note": "",
        },
    }
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
