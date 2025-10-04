from pydantic import BaseModel, Field, validator
from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import Literal, Any, Mapping
from datetime import datetime, timezone

Scope = Literal["site","slot","page","grid","tile","component"]

def utc_now_iso() -> str:
    """UTC timestamp in RFC3339/ISO8601 with 'Z'."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class EventEnvelope(BaseModel):
    scope: Scope
    type: str
    page_id: str | None
    slot: str | None
    tile_id: str | None
    ts: str
    request_id: str
    target: dict[str, Any] | None
    payload: dict[str, Any] | None

# Optional server responses

class Ack(BaseModel):
    ok: bool
    request_id: str
    code: str = "ok"
    message: str = ""

def make_ack(request_id: str, message: str = "") -> Ack:
    return Ack(ok=True, request_id=request_id, code="ok", message=message)

class ErrorAck(BaseModel):
    ok: bool
    request_id: str
    code: str
    message: str

def make_error(request_id: str, code: str, message: str) -> ErrorAck:
    return ErrorAck(ok=False, request_id=request_id, code=code, message=message)
