import pytest
from pydantic import BaseModel
from autoapi.v3.types import Column, String
from autoapi.v3 import op_alias, op_ctx
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.orm.tables import Base
from .test_op_ctx_behavior import setup_api


@pytest.mark.i9n
def test_op_ctx_alias_create_examples(sync_db_session):
    _, get_db = sync_db_session

    class Person(Base, GUIDPk):
        __tablename__ = "people"
        __resource__ = "person"
        name = Column(String, info={"autoapi": {"examples": ["Alice"]}})

        @op_ctx(alias="register", target="create", arity="collection")
        def register(cls, ctx):  # pragma: no cover - logic irrelevant
            pass

    app, _ = setup_api(Person, get_db)
    spec = app.openapi()
    _ = spec["paths"]["/person/register"]["post"]
    req_props = spec["components"]["schemas"]["PersonRegisterRequest"]["properties"]
    resp_props = spec["components"]["schemas"]["PersonRegisterResponse"]["properties"]
    assert req_props["name"]["examples"][0] == "Alice"
    assert resp_props["name"]["examples"][0] == "Alice"


@pytest.mark.i9n
def test_op_ctx_alias_inherits_canonical_schemas(sync_db_session):
    _, get_db = sync_db_session

    class CreateReq(BaseModel):
        info: str

    class CreateResp(BaseModel):
        info: str

    @op_alias(
        alias="create",
        target="create",
        request_model=CreateReq,
        response_model=CreateResp,
    )
    class Person(Base, GUIDPk):
        __tablename__ = "people2"
        __resource__ = "person2"
        name = Column(String)

        @op_ctx(alias="register", target="create", arity="collection")
        def register(cls, ctx):  # pragma: no cover - logic irrelevant
            pass

    setup_api(Person, get_db)
    assert set(Person.schemas.register.in_.model_fields) == {"info"}
    assert set(Person.schemas.register.out.model_fields) == {"info"}
