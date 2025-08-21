import asyncio
import os
import subprocess
import tempfile
import shutil
import pytest

from swarmauri_signing_ssh import SshEnvelopeSigner


def _make_key():
    tmpdir = tempfile.mkdtemp()
    priv = os.path.join(tmpdir, "id_ed25519")
    subprocess.check_call(
        ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", priv],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return priv, tmpdir


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = SshEnvelopeSigner()
    priv, tmpdir = _make_key()
    key = {"kind": "path", "priv": priv}
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    try:
        benchmark(lambda: asyncio.run(_sign()))
    finally:
        shutil.rmtree(tmpdir)
