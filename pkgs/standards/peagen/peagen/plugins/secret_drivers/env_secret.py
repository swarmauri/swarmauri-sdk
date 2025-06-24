import os
from pathlib import Path
from typing import Iterable

from .autogpg_secretdriver import AutoGpgDriver


class EnvSecret:
    """Simple secret provider that also delegates key management to GPG."""

    def __init__(
        self,
        prefix: str | None = None,
        *,
        key_dir: Path | None = None,
        passphrase: str | None = None,
    ) -> None:
        self.prefix = prefix or ""
        self._driver = AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)

    # ─── Environment helper ────────────────────────────────────────────
    def get(self, name: str) -> str:
        var = f"{self.prefix}{name}"
        val = os.getenv(var)
        if val is None:
            raise KeyError(f"Environment variable {var} not set")
        return val

    # ─── SecretDriver API delegation ───────────────────────────────────
    def encrypt(self, plaintext: bytes, recipients: Iterable[str]) -> bytes:
        return self._driver.encrypt(plaintext, recipients)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self._driver.decrypt(ciphertext)

    @staticmethod
    def decrypt_and_verify(
        ciphertext: bytes,
        priv_key: str | Path,
        user_pub: str | Path,
        passphrase: str | None = None,
    ) -> bytes:
        return AutoGpgDriver.decrypt_and_verify(
            ciphertext, priv_key, user_pub, passphrase
        )

    def list_keys(self) -> dict[str, str]:
        return self._driver.list_keys()

    def export_public_key(self, fingerprint: str, fmt: str = "armor") -> str:
        return self._driver.export_public_key(fingerprint, fmt)

    def add_key(
        self,
        public_key: Path,
        *,
        private_key: Path | None = None,
        name: str | None = None,
    ) -> dict:
        return self._driver.add_key(public_key, private_key=private_key, name=name)

    # expose key_dir and passphrase for _get_driver convenience
    @property
    def key_dir(self) -> Path:
        return self._driver.key_dir

    @key_dir.setter
    def key_dir(self, value: Path) -> None:
        self._driver.key_dir = Path(value)
        self._driver.priv_path = self._driver.key_dir / "private.asc"
        self._driver.pub_path = self._driver.key_dir / "public.asc"

    @property
    def priv_path(self) -> Path:
        return self._driver.priv_path

    @priv_path.setter
    def priv_path(self, value: Path) -> None:
        self._driver.priv_path = Path(value)

    @property
    def pub_path(self) -> Path:
        return self._driver.pub_path

    @pub_path.setter
    def pub_path(self, value: Path) -> None:
        self._driver.pub_path = Path(value)

    @property
    def passphrase(self) -> str | None:
        return self._driver.passphrase

    @passphrase.setter
    def passphrase(self, value: str | None) -> None:
        self._driver.passphrase = value
