"""Smoother Swarmauri/Tigrbl integration with direct model returns.

This example focuses on a lower-friction pattern:
- Reuse concrete Swarmauri subclasses (`HumanMessage`) directly.
- Use Tigrbl hooks + default `create` persistence to normalize payloads.
- Model a Conversation↔Message relationship with built-in persistence.
- Expose an op that returns `HumanMessage.model_validate_json(...)` directly.
- Keep request/response schemas free of extra `json_schema` payload fields.
- Mount OpenAPI and OpenRPC from the same model + op metadata.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from tigrbl import Base, TigrblApp, engine_ctx, hook_ctx, include_model, op_ctx
from tigrbl.column import F, IO, S, acol
from tigrbl.column.storage_spec import ForeignKeySpec
from tigrbl.system import build_openrpc_spec, mount_openapi, mount_openrpc
from tigrbl.types import JSON, Mapped, String, relationship

from swarmauri_standard.messages.HumanMessage import HumanMessage


class ValidateHumanMessageIn(BaseModel):
    """Minimal RPC/REST input schema."""

    message_json: str = Field(
        ...,
        description="Serialized HumanMessage JSON.",
    )


@engine_ctx(kind="sqlite", mode="memory")
class Conversation(Base):
    """Top-level container for persisted SmoothMessage records."""

    __tablename__ = "conversations"

    id: Mapped[str] = acol(storage=S(String, primary_key=True), field=F(), io=IO())
    title: Mapped[str] = acol(storage=S(String, nullable=False), field=F(), io=IO())

    messages: Mapped[list["SmoothMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


@engine_ctx(kind="sqlite", mode="memory")
class SmoothMessage(Base):
    """Persisted bridge model using Tigrbl defaults + Swarmauri validation."""

    __tablename__ = "smooth_messages"

    id: Mapped[str] = acol(storage=S(String, primary_key=True), field=F(), io=IO())
    conversation_id: Mapped[str] = acol(
        storage=S(String, fk=ForeignKeySpec("conversations.id"), nullable=False),
        field=F(),
        io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
    )
    message_json: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(),
        io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
    )
    type: Mapped[str] = acol(storage=S(String), field=F(), io=IO())
    role: Mapped[str] = acol(storage=S(String), field=F(), io=IO())
    content: Mapped[dict[str, Any] | list[Any] | str] = acol(
        storage=S(JSON),
        field=F(),
        io=IO(),
    )
    normalized_json: Mapped[str] = acol(storage=S(String), field=F(), io=IO())

    conversation: Mapped[Conversation] = relationship(back_populates="messages")

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def normalize_create_payload(cls, ctx: dict[str, Any]) -> None:
        """Hydrate persisted fields before built-in create persistence runs."""

        payload = ctx["request"].payload
        msg = HumanMessage.model_validate_json(payload["message_json"])
        payload["type"] = msg.type
        payload["role"] = msg.role
        payload["content"] = msg.content
        payload["normalized_json"] = msg.model_dump_json()

    @op_ctx(
        alias="validate",
        target="list",
        arity="collection",
        rest=True,
        request_schema=ValidateHumanMessageIn,
        response_schema=HumanMessage,
        persist="never",
    )
    async def validate(cls, ctx: dict[str, Any]) -> HumanMessage:
        """Return the concrete Swarmauri model directly from raw JSON."""

        raw = ctx["request"].payload["message_json"]
        return HumanMessage.model_validate_json(raw)


app = TigrblApp(title="Swarmauri/Tigrbl Smooth Bridge", version="0.1.0")
include_model(app, Conversation)
include_model(app, SmoothMessage)

mount_openapi(app, path="/openapi.json")
mount_openrpc(app, path="/openrpc.json")

CONVERSATION_DEFAULT_OPS = [spec.alias for spec in Conversation.ops.all]
MESSAGE_DEFAULT_OPS = [spec.alias for spec in SmoothMessage.ops.all]
VALIDATE_IN_SCHEMA = ValidateHumanMessageIn.model_json_schema()
VALIDATE_OUT_SCHEMA = HumanMessage.model_json_schema()
OPENAPI_SPEC = app.openapi()
OPENRPC_SPEC = build_openrpc_spec(app)
