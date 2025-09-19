import pytest
from pydantic import BaseModel

from tigrbl import schema_ctx
from tigrbl.config.constants import TIGRBL_SCHEMA_DECLS_ATTR


def test_schema_ctx_internal_binding_attaches_decl_to_schema():
    class Widget:
        @schema_ctx(alias="Search", kind="in")
        class SearchParams(BaseModel):
            q: str

    decl = Widget.SearchParams.__tigrbl_schema_decl__
    assert decl.alias == "Search"
    assert decl.kind == "in"
    assert not hasattr(Widget, TIGRBL_SCHEMA_DECLS_ATTR)


def test_schema_ctx_external_binding_uses_for_argument():
    class Gadget:
        pass

    @schema_ctx(alias="Result", kind="out", for_=Gadget)
    class ResultSchema(BaseModel):
        id: int

    mapping = getattr(Gadget, TIGRBL_SCHEMA_DECLS_ATTR)
    assert mapping["Result"]["out"] is ResultSchema
    decl = ResultSchema.__tigrbl_schema_decl__
    assert decl.alias == "Result"
    assert decl.kind == "out"


def test_schema_ctx_rejects_non_class_targets():
    decorator = schema_ctx(alias="Anything")

    with pytest.raises(TypeError):
        decorator(42)  # type: ignore[arg-type]
