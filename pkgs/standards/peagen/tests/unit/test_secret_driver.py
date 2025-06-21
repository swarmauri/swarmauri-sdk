from __future__ import annotations
from peagen.secrets import AutoGpgDriver


def test_keygen_and_encrypt_decrypt(tmp_path):
    drv = AutoGpgDriver(key_dir=tmp_path)
    plaintext = b"hello"
    cipher = drv.encrypt(plaintext, [])
    out = drv.decrypt(cipher)
    assert out == plaintext


def test_sign_multi_recipient(tmp_path):
    drv1 = AutoGpgDriver(key_dir=tmp_path / "a")
    drv2 = AutoGpgDriver(key_dir=tmp_path / "b")
    cipher = drv1.encrypt(b"secret", [str(drv2.pub_path)])
    # drv2 should decrypt
    out = drv2.decrypt(cipher)
    assert out == b"secret"
