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
- [ ] Rename `APIRouter` to `Router`, then inherit `Router` into `TigrblApi` and
  `TigrblApp`.
- [ ] Make `openapi.json` a system-mountable endpoint, mounted by default.
- [ ] Support middleware registration (TigrblApp only).
- [ ] Support `favicon.ico` endpoint.
- [ ] Provide an OpenRPC UI HTML endpoint.
- [ ] Ensure built-in routes can all be installed in one place.
- [ ] Provide dependency handling in the new router stack.

## Runtime internals placement

- [ ] Decide where to host `_asgi_app`, `__call__`, `_request_from_wsgi`,
  `_request_from_asgi`, `_dispatch`, `_call_handler`, `_resolve_handler_kwargs`,
  and `_invoke_dependency`.
