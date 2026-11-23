import asyncio
import os
import subprocess
import tempfile
import shutil

from swarmauri_signing_ssh import SshEnvelopeSigner


def _make_key():
    tmpdir = tempfile.mkdtemp()
    priv = os.path.join(tmpdir, "id_ed25519")
    subprocess.check_call(
        ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", priv],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    with open(priv + ".pub", "r", encoding="utf-8") as f:
        pub = f.read().strip()
    return priv, pub, tmpdir


async def _sign_and_verify() -> bool:
    signer = SshEnvelopeSigner()
    priv, pub, tmpdir = _make_key()
    try:
        key = {"kind": "path", "priv": priv, "identity": "tester"}
        payload = b"unit-test"
        sigs = await signer.sign_bytes(key, payload)
        ok = await signer.verify_bytes(
            payload, sigs, opts={"pubkeys": [pub], "identity": "tester"}
        )
        return ok
    finally:
        shutil.rmtree(tmpdir)


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())
