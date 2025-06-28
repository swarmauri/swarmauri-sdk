from peagen.protocols import (
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
            "task": {
                "tenant_id": "01234567-89ab-cdef-0123-456789abcdef",
                "git_reference_id": "fedcba98-7654-3210-fedc-ba9876543210",
                "pool": "default",
                "payload": {"action": "demo"},
                "status": "queued",
                "note": "",
                "spec_hash": "dummy",
                "id": "11111111-2222-3333-4444-555555555555",
                "last_modified": "2024-01-01T00:00:00Z",
            }
        },
    }
    req = parse_request(raw)
    PModel = _registry.params_model(req.method)
    params = PModel.model_validate(req.params)
    assert params.task.pool == "default"
    res = Response.ok(id=req.id, result={"task_id": "ABCDEFGHIJKL"})
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
