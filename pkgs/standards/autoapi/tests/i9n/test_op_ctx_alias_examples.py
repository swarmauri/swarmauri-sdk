import pytest
from autoapi.v3.types import Column, String
from autoapi.v3 import op_ctx
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
