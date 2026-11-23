"""Strict JSON invocation encoding shared by local and HTTP delivery."""

import json
from dataclasses import asdict

from swarmauri_core.invocations import InvocationRequest, InvocationResult
from swarmauri_core.permissions import Permission


def encode_request(request):
    return json.dumps(asdict(request), sort_keys=True).encode()


def decode_request(body):
    data = json.loads(body)
    expected = {
        "invocation_id",
        "edge_id",
        "task_id",
        "operation",
        "permission",
        "arguments",
        "parent_execution_id",
    }
    if not isinstance(data, dict) or set(data) != expected:
        raise ValueError("Invalid invocation envelope")
    if not isinstance(data["arguments"], dict):
        raise ValueError("Arguments must be a mapping")
    for name in ("invocation_id", "edge_id", "task_id", "operation"):
        if not isinstance(data[name], str) or not data[name]:
            raise ValueError("Invalid invocation identity")
    data["permission"] = Permission(**data["permission"])
    return InvocationRequest(**data)


def encode_result(result):
    return json.dumps(asdict(result)).encode()


def decode_result(body, expected_id):
    data = json.loads(body)
    if set(data) != {"invocation_id", "value"}:
        raise ValueError("Invalid invocation result")
    if data["invocation_id"] != expected_id:
        raise ValueError("Invocation result identity mismatch")
    return InvocationResult(**data)
