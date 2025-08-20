import pytest
from pydantic import BaseModel

from autoapi.v3 import schema_ctx
from autoapi.v3.bindings import build_schemas


class AliasModel:
    @schema_ctx(alias="Foo", kind="out")
    class FooOut(BaseModel):
        id: int


def test_schema_ctx_registers_alias_namespace():
    build_schemas(AliasModel, [])
    assert hasattr(AliasModel.schemas, "Foo")


class KindModel:
    @schema_ctx(alias="Bar", kind="in")
    class BarIn(BaseModel):
        id: int

    @schema_ctx(alias="Bar", kind="out")
    class BarOut(BaseModel):
        id: int


def test_schema_ctx_assigns_in_and_out_models():
    build_schemas(KindModel, [])
    assert KindModel.schemas.Bar.in_ is KindModel.BarIn
    assert KindModel.schemas.Bar.out is KindModel.BarOut


def test_schema_ctx_invalid_kind_raises_value_error():
    class Dummy:
        pass

    with pytest.raises(ValueError):

        @schema_ctx(alias="Bad", kind="sideways", for_=Dummy)
        class BadSchema(BaseModel):
            pass


class ForModel:
    pass


@schema_ctx(alias="Ext", kind="out", for_=ForModel)
class ExternalSchema(BaseModel):
    id: int


def test_schema_ctx_for_explicit_target_registration():
    build_schemas(ForModel, [])
    assert ForModel.schemas.Ext.out is ExternalSchema
