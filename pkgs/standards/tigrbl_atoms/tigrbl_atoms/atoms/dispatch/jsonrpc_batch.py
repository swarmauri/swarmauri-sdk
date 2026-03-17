from __future__ import annotations

import json
from typing import Any, Mapping


async def execute_if_jsonrpc_batch(ctx: Any) -> list[dict[str, Any]] | None:
    raw_body = getattr(ctx, "body", None)
    if isinstance(raw_body, (bytes, bytearray)):
        try:
            body = json.loads(bytes(raw_body).decode("utf-8"))
        except Exception:
            return None
    else:
        body = raw_body

    if not isinstance(body, list):
        return None

    app = getattr(ctx, "app", None)
    if app is None:
        return None

    responses: list[dict[str, Any]] = []
    for item in body:
        if not isinstance(item, Mapping):
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": None,
                }
            )
            continue

        request_id = item.get("id")
        method = item.get("method")
        params = item.get("params", {})
        if not isinstance(method, str) or "." not in method:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            )
            continue

        model_name, alias = method.split(".", 1)
        if not model_name or not alias:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            )
            continue

        try:
            result = await app.rpc_call(
                model_name,
                alias,
                params,
                db=None,
                request=getattr(ctx, "request", None),
                ctx={},
            )
            responses.append({"jsonrpc": "2.0", "result": result, "id": request_id})
        except AttributeError:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            )
        except Exception as exc:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(exc) or "Internal error",
                    },
                    "id": request_id,
                }
            )

    return responses


__all__ = ["execute_if_jsonrpc_batch"]
