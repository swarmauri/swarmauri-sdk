import asyncio
import json

from tigrbl.core.crud.params import Body, Query
from tigrbl.runtime.status.mappings import status
from tigrbl.types import Router, Depends, Request


def test_routing_and_dependency_injection():
    router = Router()

    def provide_token(request: Request):
        return request.headers.get("authorization")

    @router.post("/items/{item_id}")
    def handler(
        item_id: str,
        request: Request,
        payload=Body(...),
        q=Query(None),
        token=Depends(provide_token),
    ):
        return {
            "item_id": item_id,
            "payload": payload,
            "q": q,
            "token": token,
            "path": request.path,
        }

    req = Request(
        method="POST",
        path="/items/123",
        headers={"authorization": "Bearer token"},
        query={"q": ["hello"]},
        path_params={},
        body=b'{"name": "widget"}',
    )
    resp = asyncio.run(router._dispatch(req))
    assert resp.status_code == 200
    assert resp.body
    data = json.loads(resp.body.decode("utf-8"))
    assert data == {
        "item_id": "123",
        "payload": {"name": "widget"},
        "q": "hello",
        "token": "Bearer token",
        "path": "/items/123",
    }


def test_method_not_allowed_and_not_found():
    router = Router()

    @router.get("/healthz")
    def health():
        return {"ok": True}

    req = Request(
        method="POST",
        path="/healthz",
        headers={},
        query={},
        path_params={},
        body=b"",
    )
    resp = asyncio.run(router._dispatch(req))
    assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    missing = Request(
        method="GET",
        path="/missing",
        headers={},
        query={},
        path_params={},
        body=b"",
    )
    missing_resp = asyncio.run(router._dispatch(missing))
    assert missing_resp.status_code == status.HTTP_404_NOT_FOUND
