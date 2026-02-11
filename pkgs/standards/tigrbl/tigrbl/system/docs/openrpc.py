from __future__ import annotations

from typing import Any

from ...transport.jsonrpc.openrpc import build_openrpc_spec


def mount_openrpc(
    router: Any,
    api: Any,
    *,
    path: str = "/openrpc.json",
    tags: list[str] | None = None,
) -> Any:
    def _openrpc_handler() -> dict[str, Any]:
        return build_openrpc_spec(api)

    router.add_api_route(
        path,
        endpoint=_openrpc_handler,
        methods=["GET"],
        name="openrpc_json",
        tags=list(tags) if tags else None,
        summary="OpenRPC",
        description="OpenRPC 1.2.6 schema for JSON-RPC methods.",
    )
    return router


__all__ = ["mount_openrpc"]
