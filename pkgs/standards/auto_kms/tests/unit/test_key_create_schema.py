from autoapi.v3.bindings import bind
from auto_kms.tables.key import Key


def test_key_create_schema_excludes_id():
    bind(Key)
    fields = set(Key.schemas.create.in_.model_fields.keys())
    assert "id" not in fields
    assert "name" in fields and "algorithm" in fields
    assert "status" not in fields
    vcols = {
        "kid",
        "plaintext_b64",
        "aad_b64",
        "nonce_b64",
        "alg",
        "ciphertext_b64",
        "tag_b64",
        "version",
    }
    assert fields.isdisjoint(vcols)


def test_key_encrypt_decrypt_schemas():
    bind(Key)
    encrypt_in = set(Key.schemas.encrypt.in_.model_fields.keys())
    encrypt_out = set(Key.schemas.encrypt.out.model_fields.keys())
    decrypt_in = set(Key.schemas.decrypt.in_.model_fields.keys())
    decrypt_out = set(Key.schemas.decrypt.out.model_fields.keys())

    assert {"plaintext_b64", "aad_b64", "nonce_b64", "alg"}.issubset(encrypt_in)
    assert {"kid", "ciphertext_b64", "tag_b64", "version"}.issubset(encrypt_out)
    assert {"ciphertext_b64", "nonce_b64"}.issubset(decrypt_in)
    assert {"plaintext_b64"}.issubset(decrypt_out)
