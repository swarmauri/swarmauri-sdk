"""Behavioral tests for :class:`autoapi.v3.specs.io_spec.IOSpec`.

Each test focuses on a single IOSpec attribute and verifies the side effects
across the stack – request/response schemas, ORM columns, OpenAPI emission and
SQLAlchemy integration where applicable.
"""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import Session, Mapped

from autoapi.v3.bindings.model import bind
from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.runtime.atoms.out import masking
from autoapi.v3.runtime.atoms.resolve import assemble as assemble_atom
from autoapi.v3.runtime.atoms.schema import collect_in, collect_out
from autoapi.v3.specs import IO, S, acol
from autoapi.v3.tables import Base


def _openapi_for(model: type, op: str) -> dict:
    sp = OpSpec(alias=op, target=op)
    router = _build_router(model, [sp])
    app = FastAPI()
    app.include_router(router)
    return app.openapi()


def test_in_verbs_control_request_schema_and_openapi() -> None:
    class Item(Base):
        __tablename__ = "iospec_in_verbs"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Item)
    specs = Item.__autoapi_cols__

    ctx = SimpleNamespace(specs=specs, op="create", temp={})
    collect_in.run(None, ctx)
    assert "name" in ctx.temp["schema_in"]["by_field"]

    ctx_up = SimpleNamespace(specs=specs, op="update", temp={})
    collect_in.run(None, ctx_up)
    assert "name" not in ctx_up.temp["schema_in"]["by_field"]

    spec = _openapi_for(Item, "create")
    schema = spec["components"]["schemas"]["ItemCreate"]
    assert "name" in schema["properties"]


def test_out_verbs_control_response_schema_and_openapi() -> None:
    class Item(Base):
        __tablename__ = "iospec_out_verbs"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(out_verbs=("read",)),
        )

    bind(Item)
    specs = Item.__autoapi_cols__

    ctx = SimpleNamespace(specs=specs, op="read", temp={})
    collect_out.run(None, ctx)
    assert "name" in ctx.temp["schema_out"]["by_field"]

    ctx_list = SimpleNamespace(specs=specs, op="create", temp={})
    collect_out.run(None, ctx_list)
    assert "name" not in ctx_list.temp["schema_out"]["by_field"]

    spec = _openapi_for(Item, "read")
    schema = spec["components"]["schemas"]["ItemRead"]
    assert "name" in schema["properties"]


def test_mutable_verbs_allow_updates_in_request_schema_and_storage() -> None:
    class Item(Base):
        __tablename__ = "iospec_mutable"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read", "list")),
        )

        status: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), mutable_verbs=("update",)),
        )

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    bind(Item)

    specs = Item.__autoapi_cols__
    ctx = SimpleNamespace(specs=specs, op="update", temp={})
    collect_in.run(None, ctx)
    assert "status" in ctx.temp["schema_in"]["by_field"]

    with Session(engine) as session:
        obj = Item(status="new")
        session.add(obj)
        session.commit()
        obj.status = "old"
        session.commit()
        assert session.get(Item, obj.id).status == "old"


def test_alias_in_reflected_in_request_schema_and_openapi() -> None:
    class Item(Base):
        __tablename__ = "iospec_alias_in"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), alias_in="the_name"),
        )

    bind(Item)
    specs = Item.__autoapi_cols__
    ctx = SimpleNamespace(specs=specs, op="create", temp={})
    collect_in.run(None, ctx)
    assert ctx.temp["schema_in"]["by_field"]["name"]["alias_in"] == "the_name"

    spec = _openapi_for(Item, "create")
    props = spec["components"]["schemas"]["ItemCreate"]["properties"]
    assert "the_name" in props


def test_alias_out_reflected_in_response_schema_and_openapi() -> None:
    class Item(Base):
        __tablename__ = "iospec_alias_out"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(out_verbs=("read",), alias_out="the_name"),
        )

    bind(Item)
    specs = Item.__autoapi_cols__
    ctx = SimpleNamespace(specs=specs, op="read", temp={})
    collect_out.run(None, ctx)
    assert "the_name" in ctx.temp["schema_out"]["by_field"]

    spec = _openapi_for(Item, "read")
    props = spec["components"]["schemas"]["ItemRead"]["properties"]
    assert "the_name" in props


def test_sensitive_and_redact_last_mask_response_payload() -> None:
    class Item(Base):
        __tablename__ = "iospec_sensitive"
        __allow_unmapped__ = True

        secret: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(out_verbs=("read",), sensitive=True, redact_last=2),
        )

    bind(Item)
    specs = Item.__autoapi_cols__

    ctx_schema = SimpleNamespace(specs=specs, op="read", temp={})
    collect_out.run(None, ctx_schema)
    field = ctx_schema.temp["schema_out"]["by_field"]["secret"]
    assert field["sensitive"] is True
    assert field["redact_last"] == 2

    payload = {"secret": "abcd1234"}
    ctx_mask = SimpleNamespace(specs=specs, temp={"response_payload": payload})
    masking.run(SimpleNamespace(), ctx_mask)
    assert payload["secret"].endswith("34") and payload["secret"].startswith("•")


def test_filter_ops_exposed_in_list_params() -> None:
    class Item(Base):
        __tablename__ = "iospec_filter_ops"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String),
            io=IO(out_verbs=("read", "list"), filter_ops=("eq", "like")),
        )

    bind(Item)
    from autoapi.v3.bindings.rest import _build_list_params

    params_model = _build_list_params(Item)
    fields = params_model.model_fields
    assert "name" in fields
    assert "name__like" in fields


def test_sortable_field_exposed_in_list_params() -> None:
    class Item(Base):
        __tablename__ = "iospec_sortable"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String),
            io=IO(out_verbs=("read", "list"), sortable=True),
        )

    bind(Item)
    from autoapi.v3.bindings.rest import _build_list_params

    params_model = _build_list_params(Item)
    assert "sort" in params_model.model_fields


def test_allow_in_callable_filters_request_schema() -> None:
    def allow_in(verb: str, ctx: dict) -> bool:
        return verb == "create"

    class Item(Base):
        __tablename__ = "iospec_allow_in"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String),
            io=IO(in_verbs=("create", "update"), allow_in=allow_in),
        )

    bind(Item)
    specs = Item.__autoapi_cols__

    ctx_create = SimpleNamespace(specs=specs, op="create", temp={})
    collect_in.run(None, ctx_create)
    assert "name" in ctx_create.temp["schema_in"]["by_field"]

    ctx_update = SimpleNamespace(specs=specs, op="update", temp={})
    collect_in.run(None, ctx_update)
    assert "name" not in ctx_update.temp["schema_in"]["by_field"]


def test_allow_out_callable_filters_response_schema() -> None:
    def allow_out(verb: str, ctx: dict) -> bool:
        return verb == "read"

    class Item(Base):
        __tablename__ = "iospec_allow_out"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String),
            io=IO(out_verbs=("read", "list"), allow_out=allow_out),
        )

    bind(Item)
    specs = Item.__autoapi_cols__

    ctx_read = SimpleNamespace(specs=specs, op="read", temp={})
    collect_out.run(None, ctx_read)
    assert "name" in ctx_read.temp["schema_out"]["by_field"]

    ctx_list = SimpleNamespace(specs=specs, op="list", temp={})
    collect_out.run(None, ctx_list)
    assert "name" not in ctx_list.temp["schema_out"]["by_field"]


def test_default_factory_applies_when_value_absent() -> None:
    class Item(Base):
        __tablename__ = "iospec_default_factory"
        __allow_unmapped__ = True

        nickname: Mapped[str] = acol(
            storage=S(type_=String),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
            default_factory=lambda ctx: "anon",
        )

    bind(Item)
    specs = Item.__autoapi_cols__

    payload: dict = {}
    ctx = SimpleNamespace(specs=specs, payload=payload, temp={})
    assemble_atom.run(None, ctx)
    assert payload["nickname"] == "anon"
