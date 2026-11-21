import asyncio
import subprocess
import tempfile
from pathlib import Path

from swarmauri_signing_ssh import SshEnvelopeSigner


async def main() -> bool:
    signer = SshEnvelopeSigner()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        priv_path = tmpdir_path / "id_ed25519"
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(priv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pubkey_line = (
            priv_path.with_suffix(".pub").read_text(encoding="utf-8").strip()
        )

        key = {
            "kind": "path",
            "priv": str(priv_path),
            "identity": "readme-demo",
        }
        payload = b"hello ssh signatures"

        signatures = await signer.sign_bytes(key, payload)
        return await signer.verify_bytes(
            payload,
            signatures,
            opts={"pubkeys": [pubkey_line], "identity": "readme-demo"},
        )


if __name__ == "__main__":  # pragma: no cover - README execution path
    print(asyncio.run(main()))
