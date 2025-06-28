from peagen.protocols import (
    Request,
    parse_request,
    TASK_SUBMIT,
    params_model,
    result_model,
)


def test_parse_request_structural() -> None:
    raw = {"jsonrpc": "2.0", "id": 1, "method": "Task.submit.v1", "params": {}}
    req = parse_request(raw)
    assert isinstance(req, Request)
    assert req.method == "Task.submit.v1"


def test_registry_models() -> None:
    assert params_model(TASK_SUBMIT).__name__ == "SubmitParams"
    assert result_model(TASK_SUBMIT).__name__ == "SubmitResult"
