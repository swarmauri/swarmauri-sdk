import asyncio
import json

from tigrbl.deps import stdapi


def test_routing_and_dependency_injection():
    router = stdapi.APIRouter()

    def provide_token(request: stdapi.Request):
        return request.headers.get("authorization")

    @router.post("/items/{item_id}")
    def handler(
        item_id: str,
        request: stdapi.Request,
        payload=stdapi.Body(...),
        q=stdapi.Query(None),
        token=stdapi.Depends(provide_token),
    ):
        return {
            "item_id": item_id,
            "payload": payload,
            "q": q,
            "token": token,
            "path": request.path,
        }

    req = stdapi.Request(
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
    router = stdapi.APIRouter()

    @router.get("/healthz")
    def health():
        return {"ok": True}

    req = stdapi.Request(
        method="POST",
        path="/healthz",
        headers={},
        query={},
        path_params={},
        body=b"",
    )
    resp = asyncio.run(router._dispatch(req))
    assert resp.status_code == stdapi.status.HTTP_405_METHOD_NOT_ALLOWED

    missing = stdapi.Request(
        method="GET",
        path="/missing",
        headers={},
        query={},
        path_params={},
        body=b"",
    )
    missing_resp = asyncio.run(router._dispatch(missing))
    assert missing_resp.status_code == stdapi.status.HTTP_404_NOT_FOUND
