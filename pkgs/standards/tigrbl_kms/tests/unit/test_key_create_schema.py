from tigrbl.bindings import bind
from tigrbl_kms.orm import Key


def test_key_create_schema_excludes_id():
    bind(Key)
    fields = set(Key.schemas.create.in_.model_fields.keys())
    assert "id" not in fields
    assert "name" in fields and "algorithm" in fields
    assert "status" not in fields
    for vcol in (
        "kid",
        "plaintext_b64",
        "aad_b64",
        "nonce_b64",
        "alg",
        "ciphertext_b64",
        "tag_b64",
        "version",
    ):
        assert vcol not in fields
