from autoapi.v3.bindings import bind
from auto_kms.tables.key import Key


def test_key_encrypt_decrypt_vcols():
    bind(Key)
    enc_in = set(Key.schemas.encrypt.in_.model_fields.keys())
    assert {"plaintext_b64", "aad_b64", "nonce_b64", "alg"} <= enc_in
    assert "ciphertext_b64" not in enc_in

    enc_out = set(Key.schemas.encrypt.out.model_fields.keys())
    assert {
        "kid",
        "nonce_b64",
        "ciphertext_b64",
        "tag_b64",
        "alg",
        "version",
    } <= enc_out
    assert "plaintext_b64" not in enc_out

    dec_in = set(Key.schemas.decrypt.in_.model_fields.keys())
    assert {"ciphertext_b64", "aad_b64", "nonce_b64", "tag_b64", "alg"} <= dec_in
    assert "plaintext_b64" not in dec_in

    dec_out = set(Key.schemas.decrypt.out.model_fields.keys())
    assert {"plaintext_b64"} <= dec_out
    assert "ciphertext_b64" not in dec_out

    read_out = set(Key.schemas.read.out.model_fields.keys())
    for fld in [
        "plaintext_b64",
        "ciphertext_b64",
        "tag_b64",
        "nonce_b64",
        "alg",
        "version",
    ]:
        assert fld not in read_out
    assert "kid" in read_out
