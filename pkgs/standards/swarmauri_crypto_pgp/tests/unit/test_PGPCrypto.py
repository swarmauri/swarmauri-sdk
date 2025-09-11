import pytest
from enum import Enum

from swarmauri_crypto_pgp import PGPCrypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


@pytest.fixture
def pgp_crypto():
    return PGPCrypto()


@pytest.mark.unit
def test_ubc_resource(pgp_crypto):
    assert pgp_crypto.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(pgp_crypto):
    assert pgp_crypto.type == "PGPCrypto"


@pytest.mark.unit
def test_serialization(pgp_crypto):
    assert (
        pgp_crypto.id == PGPCrypto.model_validate_json(pgp_crypto.model_dump_json()).id
    )


@pytest.mark.asyncio
async def test_aead_encrypt_decrypt_roundtrip(pgp_crypto):
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x11" * 32,
    )

    pt = b"hello world"
    ct = await pgp_crypto.encrypt(sym, pt)
    rt = await pgp_crypto.decrypt(sym, ct)
    assert rt == pt


class DummyAlg(str, Enum):
    AES256_GCM = "AES256_GCM"


@pytest.mark.asyncio
async def test_enum_algorithm_normalized(pgp_crypto):
    sym = KeyRef(
        kid="sym2",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x22" * 32,
    )

    pt = b"enum alg"
    ct = await pgp_crypto.encrypt(sym, pt, alg=DummyAlg.AES256_GCM)
    assert ct.alg == "AES-256-GCM"
    rt = await pgp_crypto.decrypt(sym, ct)
    assert rt == pt


@pytest.mark.asyncio
async def test_encrypt_for_many_and_unwrap(pgp_crypto, tmp_path):
    gnupg = pytest.importorskip("gnupg")
    import os
    import shutil

    if shutil.which("gpg") is None:
        pytest.skip("gpg binary not found; skipping OpenPGP integration test")

    # Create ephemeral GPG home and generate RSA key
    gpg_home = tmp_path / "gpg"
    gpg_home.mkdir(parents=True, exist_ok=True)
    os.chmod(gpg_home, 0o700)
    gpg = gnupg.GPG(
        gnupghome=str(gpg_home),
        options=["--pinentry-mode", "loopback", "--batch", "--yes", "--no-tty"],
        use_agent=False,
    )

    key_input = gpg.gen_key_input(
        key_type="RSA",
        key_length=2048,
        name_real="Test PGP",
        name_email="test@example.com",
        passphrase="",
    )
    key = gpg.gen_key(key_input)
    if not key.fingerprint:
        pytest.skip("GPG key generation failed in this environment; skipping test")

    pub_asc = gpg.export_keys(key.fingerprint)
    priv_asc = gpg.export_keys(key.fingerprint, secret=True, passphrase="")

    recipient = KeyRef(
        kid="pgp1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pub_asc.encode(),
        material=priv_asc.encode(),
    )

    env = await pgp_crypto.encrypt_for_many([recipient], b"secret")
    assert env.enc_alg == "AES-256-GCM"
    assert env.nonce and env.ct and env.tag
    assert len(env.recipients) == 1

    wrapped = await pgp_crypto.wrap(recipient)
    unwrapped = await pgp_crypto.unwrap(recipient, wrapped)
    assert isinstance(unwrapped, bytes)
    assert len(unwrapped) == 32
