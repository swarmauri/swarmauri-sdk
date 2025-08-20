from autoapi.v3.bindings import bind
from auto_kms.tables.key import Key


def test_key_create_schema_excludes_id():
    bind(Key)
    fields = set(Key.schemas.create.in_.model_fields.keys())
    assert "id" not in fields
    assert "name" in fields and "algorithm" in fields
    assert "status" not in fields
