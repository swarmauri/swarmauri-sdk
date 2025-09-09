from tigrbl.v3.bindings import bind
from auto_kms.orm import Key


def test_key_encrypt_decrypt_schemas():
    bind(Key)
    enc_in = set(Key.schemas.encrypt.in_.model_fields.keys())
    enc_out = set(Key.schemas.encrypt.out.model_fields.keys())
    dec_in = set(Key.schemas.decrypt.in_.model_fields.keys())
    dec_out = set(Key.schemas.decrypt.out.model_fields.keys())

    assert {"plaintext_b64", "aad_b64", "nonce_b64", "alg"} <= enc_in
    assert {
        "kid",
        "aad_b64",
        "nonce_b64",
        "alg",
        "ciphertext_b64",
        "tag_b64",
        "version",
    } <= enc_out
    assert {"aad_b64", "nonce_b64", "alg", "ciphertext_b64", "tag_b64"} <= dec_in
    assert {"plaintext_b64"} <= dec_out
