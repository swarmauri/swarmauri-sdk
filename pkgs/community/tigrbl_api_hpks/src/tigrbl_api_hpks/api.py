"""API construction helpers for the HPKS application."""

from __future__ import annotations

import datetime as dt
from typing import Any, AsyncIterator

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from .ops import pks as pks_ops
from .tables import OpenPGPKey

HPKS_CORS_HEADERS = {"Access-Control-Allow-Origin": "*"}


def _cors_headers() -> dict[str, str]:
    return dict(HPKS_CORS_HEADERS)


def _normalize_fingerprint(value: str) -> str:
    stripped = value.strip().replace(" ", "")
    if stripped.lower().startswith("0x"):
        stripped = stripped[2:]
    return stripped.upper()


def build_app(
    *, async_mode: bool = True, engine_cfg: dict[str, Any] | None = None
) -> TigrblApp:
    """Create a :class:`TigrblApp` instance with HPKS routes bound."""

    cfg = engine_cfg or mem(async_=async_mode)
    app = TigrblApp(engine=build_engine(cfg))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_models([OpenPGPKey], base_prefix="/admin")
    app.attach_diagnostics(prefix="/system")

    router = APIRouter(prefix="/pks")

    async def get_session() -> AsyncIterator[Any]:
        async with app.engine.asession() as session:
            yield session

    def _not_found(detail: str = "Not found") -> HTTPException:
        return HTTPException(status_code=404, detail=detail, headers=HPKS_CORS_HEADERS)

    @router.post("/add")
    async def legacy_add(
        *, keytext: str = Form(...), db: Any = Depends(get_session)
    ) -> PlainTextResponse:
        try:
            await pks_ops.ingest_armored(db=db, armored=keytext)
        except ValueError as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=422, detail=str(exc), headers=HPKS_CORS_HEADERS
            ) from exc
        return PlainTextResponse("OK\n", headers=_cors_headers())

    @router.get("/lookup")
    async def legacy_lookup(
        *,
        op: str,
        search: str,
        options: str | None = None,
        db: Any = Depends(get_session),
    ) -> Response:
        op_name = op.lower()
        normalized = _normalize_fingerprint(search)
        if op_name == "index":
            results = await pks_ops.search_index(db=db, search=search)
            if not results:
                raise _not_found()
            body = pks_ops.render_legacy_index(results, search=search)
            return PlainTextResponse(body, headers=_cors_headers())
        if op_name == "get":
            if len(normalized) <= 8:
                raise _not_found()
            record = await pks_ops.lookup_by_fingerprint(db=db, fingerprint=normalized)
            if record is None:
                raise _not_found()
            return PlainTextResponse(
                record.ascii_armored,
                media_type="application/pgp-keys",
                headers=_cors_headers(),
            )
        if op_name == "hget":
            record = await pks_ops.lookup_by_email_hash(db=db, email_hash=search)
            if record is None:
                raise _not_found()
            return PlainTextResponse(
                record.ascii_armored,
                media_type="application/pgp-keys",
                headers=_cors_headers(),
            )
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported legacy op '{op}'",
            headers=HPKS_CORS_HEADERS,
        )

    @router.post("/{fingerprint}")
    async def merge_fingerprint(
        *,
        fingerprint: str,
        payload: dict[str, Any] = Body(...),
        db: Any = Depends(get_session),
    ) -> JSONResponse:
        try:
            record = await pks_ops.merge_json_payload(
                db=db, fingerprint=fingerprint, payload=payload
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=422, detail=str(exc), headers=HPKS_CORS_HEADERS
            ) from exc
        return JSONResponse(pks_ops.to_v2_document(record), headers=_cors_headers())

    @router.post("/v2/add")
    async def v2_add(request: Request, db: Any = Depends(get_session)) -> JSONResponse:
        content_type = request.headers.get("Content-Type", "")
        if "application/pgp-keys" not in content_type:
            raise HTTPException(
                status_code=415,
                detail="Content-Type must be application/pgp-keys",
                headers=HPKS_CORS_HEADERS,
            )
        bundle = await request.body()
        if not bundle:
            raise HTTPException(
                status_code=400, detail="Empty payload", headers=HPKS_CORS_HEADERS
            )
        try:
            summary = await pks_ops.ingest_binary(db=db, bundle=bundle)
        except ValueError as exc:
            raise HTTPException(
                status_code=422, detail=str(exc), headers=HPKS_CORS_HEADERS
            ) from exc
        return JSONResponse(summary, status_code=202, headers=_cors_headers())

    @router.get("/v2/index/{query}")
    async def v2_index(query: str, db: Any = Depends(get_session)) -> JSONResponse:
        results = await pks_ops.search_index(db=db, search=query)
        if not results:
            raise _not_found()
        payload = [pks_ops.to_v2_document(rec) for rec in results]
        return JSONResponse(payload, headers=_cors_headers())

    @router.get("/v2/vfpget/{fingerprint}")
    async def vfpget(fingerprint: str, db: Any = Depends(get_session)) -> Response:
        record = await pks_ops.lookup_by_fingerprint(db=db, fingerprint=fingerprint)
        if record is None:
            raise _not_found()
        return Response(
            content=record.binary,
            media_type="application/pgp-keys; encoding=binary",
            headers=_cors_headers(),
        )

    @router.get("/v2/kidget/{keyid}")
    async def kidget(keyid: str, db: Any = Depends(get_session)) -> Response:
        record = await pks_ops.lookup_by_keyid(db=db, key_id=keyid)
        if record is None or (record.version and record.version > 4):
            raise _not_found()
        return Response(
            content=record.binary,
            media_type="application/pgp-keys; encoding=binary",
            headers=_cors_headers(),
        )

    @router.get("/v2/authget/{identifier}")
    async def authget(identifier: str, db: Any = Depends(get_session)) -> Response:
        matches = await pks_ops.search_index(db=db, search=identifier)
        lowered = identifier.lower()
        record = next(
            (
                rec
                for rec in matches
                if any(lowered == email for email in rec.emails or [])
            ),
            None,
        )
        if record is None:
            raise _not_found()
        return Response(
            content=record.binary,
            media_type="application/pgp-keys; encoding=binary",
            headers=_cors_headers(),
        )

    @router.get("/v2/prefixlog/{since}")
    async def prefixlog_route(
        since: str, db: Any = Depends(get_session)
    ) -> PlainTextResponse:
        try:
            parsed = dt.datetime.fromisoformat(since)
        except ValueError:
            try:
                parsed = dt.datetime.strptime(since, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid prefixlog cursor",
                    headers=HPKS_CORS_HEADERS,
                ) from None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        prefixes = await pks_ops.prefix_log(db=db, since=parsed)
        body = "\r\n".join(prefixes)
        return PlainTextResponse(body, headers=_cors_headers())

    @router.post("/v2/tokensend")
    async def tokensend(_: Request) -> Response:
        return Response(status_code=501, headers=_cors_headers())

    app.include_router(router)
    return app


__all__ = ["build_app"]
