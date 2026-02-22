# Future Tigrbl Tasks

Track the items below and **check them off once completed** so we have a single
source of truth for the remaining follow-ups.

## Architecture notes

- [ ] Move `Response` and response handling into the `response` domain.
- [ ] Move `Request` into the `request` domain.
- [ ] Move `HTTPException` and HTTP status utilities into `transport`.

## Placement decisions to resolve

- [ ] Security helpers need a dedicated home (define the module and owner).
- [ ] `Param` helpers might live in `core.crud` (confirm the final location).
- [ ] `Body` helpers location (align with `Param`/request handling).
- [ ] `Path` helpers location (align with routing/transport decisions).
- [ ] `Header` helpers location (align with request/transport decisions).
- [ ] `Handler` utilities might live in `core.crud` (confirm the final location).
- [ ] `Route` structure location (routing/transport decision).
- [ ] Rename `APIRouter` to `Router`, then inherit `Router` into `TigrblRouter` and
  `TigrblApp`.
- [ ] Make `openapi.json` a system-mountable endpoint, mounted by default.
- [ ] Support middleware registration (TigrblApp only).
- [ ] Support `favicon.ico` endpoint.
- [ ] Provide an OpenRPC UI HTML endpoint.
- [ ] Ensure built-in routes can all be installed in one place.
- [ ] Provide dependency handling in the new router stack.
- [ ] Remove the `LegacyApi` class from stdapi, then update `TigrblApp` to import
  `APIRouter` instead; add `router` and `middleware` attributes and implement
  `add_middleware` on `TigrblApp`.
- [ ] Create a mountable favicon system endpoint; mount it by default on
  `TigrblApp` and offer a parameter for setting `FAVICON_PATH`.

## Runtime internals placement

- [ ] Decide where to host `_asgi_app`, `__call__`, `_request_from_wsgi`,
  `_request_from_asgi`, `_dispatch`, `_call_handler`, `_resolve_handler_kwargs`,
  and `_invoke_dependency`.

## Runtime behavior and compatibility fixes

- [ ] Add lifespan support for the ASGI stack.
- [ ] Implement support for `__enter__`/`__aenter__` to address
  `AttributeError: 'ASGITransport' object has no attribute '__enter__'. Did you mean: '__aenter__'?`.
- [ ] Implement support to resolve
  `AttributeError: 'Route' object has no attribute 'path'`.
- [ ] Implement support to resolve `KeyError: 'requestBody'`.
- [ ] Implement support to resolve `KeyError: 'components'`.
- [ ] Avoid shadowing Pydantic's `json` method.
- [ ] Debug and resolve
  `TypeError: APIRouter._install_builtin_routes.<locals>._openapi_handler() missing 1 required positional argument: 'req'`.
- [ ] Debug and resolve `AssertionError: assert None == [{'HTTPBearer': []}]`.
- [ ] Debug and resolve
  `TypeError: Object of type Response is not JSON serializable`.
