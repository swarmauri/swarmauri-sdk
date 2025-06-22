from __future__ import annotations
from peagen.plugins.secret_drivers import AutoGpgDriver


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


def test_decrypt_and_verify(tmp_path):
    sender = AutoGpgDriver(key_dir=tmp_path / "sender")
    recipient = AutoGpgDriver(key_dir=tmp_path / "recipient")
    cipher = sender.encrypt(b"ping", [str(recipient.pub_path)])
    out = AutoGpgDriver.decrypt_and_verify(
        cipher,
        priv_key=str(recipient.priv_path),
        user_pub=str(sender.pub_path),
    )
    assert out == b"ping"
