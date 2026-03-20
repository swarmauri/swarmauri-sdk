"""API construction helpers for the HPKS application."""

from __future__ import annotations

import datetime as dt
import os
import tempfile
from typing import Any
from urllib.parse import parse_qs

from tigrbl import Router, TigrblApp, Response, Request
from tigrbl.decorators.router import route
from tigrbl.shortcuts.engine import engine as build_engine
from tigrbl.runtime.status import HTTPException


from .ops import pks as pks_ops
from .tables import OpenPGPKey

HPKS_CORS_HEADERS = {"Access-Control-Allow-Origin": "*"}


def _normalize_fingerprint(value: str) -> str:
    stripped = value.strip().replace(" ", "")
    if stripped.lower().startswith("0x"):
        stripped = stripped[2:]
    return stripped.upper()


def _query_first(request: Request, key: str, default: str = "") -> str:
    """Extract the first value for a query parameter."""
    values = request.query.get(key, [])
    return values[0] if values else default


def _path_segment(request: Request, index: int) -> str:
    """Extract a path segment by index (0-based, after splitting on '/')."""
    parts = request.path.strip("/").split("/")
    return parts[index] if index < len(parts) else ""


def _response_text(
    content: str,
    *,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    media_type: str | None = None,
) -> Response:
    resp = Response.text(content, status_code=status_code, headers=headers)
    if media_type:
        resp.media_type = media_type
        resp.headers["content-type"] = media_type
    return resp


def _response_json(
    payload: Any,
    *,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> Response:
    return Response.json(payload, status_code=status_code, headers=headers)


def _response_binary(
    payload: bytes,
    *,
    media_type: str,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> Response:
    merged_headers = {k.lower(): v for k, v in (headers or {}).items()}
    merged_headers["content-type"] = media_type
    return Response(
        status_code=status_code,
        headers=list(merged_headers.items()),
        body=payload,
        media_type=media_type,
    )


def build_app(
    *, async_mode: bool = True, engine_cfg: dict[str, Any] | None = None
) -> TigrblApp:
    """Create a :class:`TigrblApp` instance with HPKS routes bound."""

    if engine_cfg is None:
        fd, path = tempfile.mkstemp(prefix="tigrbl_api_hpks_", suffix=".db")
        os.close(fd)
        cfg = {"kind": "sqlite", "async": async_mode, "path": path}
    else:
        cfg = engine_cfg
    app = TigrblApp(engine=build_engine(cfg))
    app.include_tables([OpenPGPKey], base_prefix="/admin")
    app.attach_diagnostics(prefix="/system")

    router = Router(prefix="/pks")

    def _not_found(detail: str = "Not found") -> HTTPException:
        return HTTPException(status_code=404, detail=detail, headers=HPKS_CORS_HEADERS)

    # ---- Legacy HKP endpoints ----

    @route(router, "/add", methods=["POST"])
    async def legacy_add(request: Request) -> Response:
        body = request.body.decode("utf-8")
        form_data = parse_qs(body, keep_blank_values=True)
        keytext = form_data.get("keytext", [""])[0]
        if not keytext:
            raise HTTPException(
                status_code=422,
                detail="keytext is required",
                headers=HPKS_CORS_HEADERS,
            )
        async with app.engine.asession() as db:
            try:
                await pks_ops.ingest_armored(db=db, armored=keytext)
            except ValueError as exc:
                raise HTTPException(
                    status_code=422, detail=str(exc), headers=HPKS_CORS_HEADERS
                ) from exc
        return _response_text("OK\n", headers=HPKS_CORS_HEADERS)

    @route(router, "/lookup", methods=["GET"])
    async def legacy_lookup(request: Request):
        op = _query_first(request, "op")
        search = _query_first(request, "search")
        op_name = op.lower()
        normalized = _normalize_fingerprint(search)
        async with app.engine.asession() as db:
            if op_name == "index":
                results = await pks_ops.search_index(db=db, search=search)
                if not results:
                    raise _not_found()
                body = pks_ops.render_legacy_index(results, search=search)
                return _response_text(body, headers=HPKS_CORS_HEADERS)
            if op_name == "get":
                if len(normalized) <= 8:
                    raise _not_found()
                record = await pks_ops.lookup_by_fingerprint(
                    db=db, fingerprint=normalized
                )
                if record is None:
                    raise _not_found()
                return _response_text(
                    record.ascii_armored,
                    media_type="application/pgp-keys",
                    headers=HPKS_CORS_HEADERS,
                )
            if op_name == "hget":
                record = await pks_ops.lookup_by_email_hash(db=db, email_hash=search)
                if record is None:
                    raise _not_found()
                return _response_text(
                    record.ascii_armored,
                    media_type="application/pgp-keys",
                    headers=HPKS_CORS_HEADERS,
                )
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported legacy op '{op}'",
            headers=HPKS_CORS_HEADERS,
        )

    # ---- V2 endpoints ----

    # Pattern: /pks/{fingerprint} — the fingerprint is the 2nd segment
    @route(router, "/{fingerprint}", methods=["POST"])
    async def merge_fingerprint(request: Request) -> Response:
        fingerprint = _path_segment(request, 1)
        payload = await request.json() or {}
        async with app.engine.asession() as db:
            try:
                record = await pks_ops.merge_json_payload(
                    db=db, fingerprint=fingerprint, payload=payload
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=422, detail=str(exc), headers=HPKS_CORS_HEADERS
                ) from exc
        return _response_json(pks_ops.to_v2_document(record), headers=HPKS_CORS_HEADERS)

    @route(router, "/v2/add", methods=["POST"])
    async def v2_add(request: Request) -> Response:
        content_type = request.headers.get("content-type", "")
        if "application/pgp-keys" not in content_type:
            raise HTTPException(
                status_code=415,
                detail="Content-Type must be application/pgp-keys",
                headers=HPKS_CORS_HEADERS,
            )
        bundle = request.body
        if not bundle:
            raise HTTPException(
                status_code=400, detail="Empty payload", headers=HPKS_CORS_HEADERS
            )
        async with app.engine.asession() as db:
            try:
                summary = await pks_ops.ingest_binary(db=db, bundle=bundle)
            except ValueError as exc:
                raise HTTPException(
                    status_code=422, detail=str(exc), headers=HPKS_CORS_HEADERS
                ) from exc
        return _response_json(summary, status_code=202, headers=HPKS_CORS_HEADERS)

    # Pattern: /pks/v2/index/{query} — the query is the 4th segment
    @route(router, "/v2/index/{query}", methods=["GET"])
    async def v2_index(request: Request) -> Response:
        query = _path_segment(request, 3)
        async with app.engine.asession() as db:
            results = await pks_ops.search_index(db=db, search=query)
        if not results:
            raise _not_found()
        payload = [pks_ops.to_v2_document(rec) for rec in results]
        return _response_json(payload, headers=HPKS_CORS_HEADERS)

    # Pattern: /pks/v2/vfpget/{fingerprint} — fingerprint is the 4th segment
    @route(router, "/v2/vfpget/{fingerprint}", methods=["GET"])
    async def vfpget(request: Request) -> Response:
        fingerprint = _path_segment(request, 3)
        async with app.engine.asession() as db:
            record = await pks_ops.lookup_by_fingerprint(db=db, fingerprint=fingerprint)
        if record is None:
            raise _not_found()
        return _response_binary(
            record.binary,
            media_type="application/pgp-keys; encoding=binary",
            headers=HPKS_CORS_HEADERS,
        )

    # Pattern: /pks/v2/kidget/{keyid} — keyid is the 4th segment
    @route(router, "/v2/kidget/{keyid}", methods=["GET"])
    async def kidget(request: Request) -> Response:
        keyid = _path_segment(request, 3)
        async with app.engine.asession() as db:
            record = await pks_ops.lookup_by_keyid(db=db, key_id=keyid)
        if record is None or (record.version and record.version > 4):
            raise _not_found()
        return _response_binary(
            record.binary,
            media_type="application/pgp-keys; encoding=binary",
            headers=HPKS_CORS_HEADERS,
        )

    # Pattern: /pks/v2/authget/{identifier} — identifier is the 4th segment
    @route(router, "/v2/authget/{identifier}", methods=["GET"])
    async def authget(request: Request) -> Response:
        identifier = _path_segment(request, 3)
        async with app.engine.asession() as db:
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
        return _response_binary(
            record.binary,
            media_type="application/pgp-keys; encoding=binary",
            headers=HPKS_CORS_HEADERS,
        )

    # Pattern: /pks/v2/prefixlog/{since} — since is the 4th segment
    @route(router, "/v2/prefixlog/{since}", methods=["GET"])
    async def prefixlog_route(request: Request) -> Response:
        since = _path_segment(request, 3)
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
        async with app.engine.asession() as db:
            prefixes = await pks_ops.prefix_log(db=db, since=parsed)
        body = "\r\n".join(prefixes)
        return _response_text(body, headers=HPKS_CORS_HEADERS)

    @route(router, "/v2/tokensend", methods=["POST"])
    async def tokensend(request: Request) -> Response:
        return Response(status_code=501, headers=list(HPKS_CORS_HEADERS.items()))

    app.include_router(router)
    return app


__all__ = ["build_app"]
