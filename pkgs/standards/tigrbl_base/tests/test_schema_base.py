from tigrbl_base._base._schema_base import SchemaBase


class WithSchemas:
    schemas = {"req": {"name": str}}


class WithoutSchemas:
    pass


def test_schema_base_collect() -> None:
    assert SchemaBase.collect(WithSchemas) == {"req": {"name": str}}
    assert SchemaBase.collect(WithoutSchemas) == {}
