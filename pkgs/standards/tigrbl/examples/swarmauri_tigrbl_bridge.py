"""Bridge Swarmauri Pydantic models into Tigrbl hooks + docs.

This example demonstrates:
- Using a concrete Swarmauri subclass (`HumanMessage`) instead of inheriting ComponentBase.
- Running a Swarmauri class factory in a Tigrbl `PRE_HANDLER` hook.
- Validating/dumping JSON via Swarmauri's Pydantic surface.
- Surfacing schemas through Tigrbl OpenAPI/OpenRPC generation.
- Keeping default Tigrbl operation verbs (`create`, `get`, `list`, `update`, `delete`).
- Attaching `engine_ctx` at model and op scopes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from tigrbl import Base, TigrblApp, engine_ctx, hook_ctx, include_model, op_ctx
from tigrbl.system import build_openrpc_spec, mount_openapi, mount_openrpc

from swarmauri_standard.factories.Factory import Factory as SwarmauriFactory
from swarmauri_standard.messages.HumanMessage import HumanMessage


class MessageEnvelopeIn(BaseModel):
    """Incoming payload used by Tigrbl schema generation."""

    message_json: str = Field(
        ...,
        description="Serialized swarmauri HumanMessage JSON payload.",
    )


class MessageEnvelopeOut(BaseModel):
    """Outgoing payload including normalized Swarmauri JSON and schema."""

    type: str
    role: str
    content: str | list[dict[str, Any]]
    swarmauri_json: str
    swarmauri_schema: dict[str, Any]


@engine_ctx(kind="sqlite", mode="memory")
class MessageEnvelope(Base):
    """Tigrbl model that stores and exposes Swarmauri message payloads."""

    __tablename__ = "message_envelopes"

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def hydrate_swarmauri_message(cls, ctx: dict[str, Any]) -> None:
        """Class-factory PRE_HANDLER hook using concrete Swarmauri subclasses."""

        payload = ctx["request"].payload
        # 1) Validate raw JSON with the concrete Swarmauri class.
        validated = HumanMessage.model_validate_json(payload["message_json"])

        # 2) Rebuild via Swarmauri class factory (no direct ComponentBase inheritance).
        factory = SwarmauriFactory()
        rebuilt = factory.create("message", validated.type, **validated.model_dump())

        # 3) Feed normalized data back into the Tigrbl request payload.
        payload["type"] = rebuilt.type
        payload["role"] = rebuilt.role
        payload["content"] = rebuilt.content
        payload["swarmauri_json"] = rebuilt.model_dump_json()
        payload["swarmauri_schema"] = HumanMessage.model_json_schema()

    @op_ctx(
        alias="preview",
        target="list",
        arity="collection",
        rest=True,
        request_schema=MessageEnvelopeIn,
        response_schema=MessageEnvelopeOut,
        persist="never",
    )
    @engine_ctx(kind="sqlite", mode="memory")
    async def preview(cls, ctx: dict[str, Any]) -> dict[str, Any]:
        """Non-persistent op that runs through normal phase + hook lifecycle."""

        payload = dict(ctx["request"].payload)
        msg = HumanMessage.model_validate_json(payload["message_json"])
        payload["type"] = msg.type
        payload["role"] = msg.role
        payload["content"] = msg.content
        payload["swarmauri_json"] = msg.model_dump_json()
        payload["swarmauri_schema"] = HumanMessage.model_json_schema()
        return payload


app = TigrblApp(title="Swarmauri/Tigrbl Bridge", version="0.1.0")
include_model(app, MessageEnvelope)

# OpenAPI + OpenRPC endpoints/document builders.
mount_openapi(app, path="/openapi.json")
mount_openrpc(app, path="/openrpc.json")

# Introspection helpers showing default verbs + custom preview verb.
DEFAULT_OPS = [spec.alias for spec in MessageEnvelope.ops.all]
OPENAPI_SPEC = app.openapi()
OPENRPC_SPEC = build_openrpc_spec(app)
