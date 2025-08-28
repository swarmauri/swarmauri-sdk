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


def create_env(message: str):
    return {"msg": message}


async def _run() -> bool:
    signer = SshEnvelopeSigner()
    priv, pub, tmpdir = _make_key()
    try:
        key = {"kind": "path", "priv": priv}
        env = create_env("hello")
        sigs = await signer.sign_envelope(key, env, canon="json")
        good = await signer.verify_envelope(
            env, sigs, canon="json", opts={"pubkeys": [pub], "identity": "default"}
        )
        bad = await signer.verify_envelope(
            {"msg": "tampered"},
            sigs,
            canon="json",
            opts={"pubkeys": [pub], "identity": "default"},
        )
        return good and not bad
    finally:
        shutil.rmtree(tmpdir)


def test_sign_and_verify_envelope_functional():
    assert asyncio.run(_run())
