from __future__ import annotations

from pathlib import Path
from typing import Iterable, Literal, Optional
import warnings

from cryptography.utils import CryptographyDeprecationWarning
import pgpy
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)

from swarmauri_base.secrets.SecretDriveBase import SecretDriveBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyDescriptor,
    KeyId,
    KeyRef,
    KeyState,
    KeyType,
    KeyUse,
    KeyVersion,
    KeyVersionInfo,
    Page,
)


warnings.filterwarnings(
    "ignore", category=CryptographyDeprecationWarning, module="pgpy.constants"
)


@ComponentBase.register_type(SecretDriveBase, "AutoGpgSecretDrive")
class AutoGpgSecretDrive(SecretDriveBase):
    type: Literal["AutoGpgSecretDrive"] = "AutoGpgSecretDrive"

    def __init__(
        self, *, key_dir: str | Path | None = None, passphrase: str | None = None
    ) -> None:
        super().__init__()
        self.key_dir = Path(key_dir or Path.home() / ".swarmauri" / "keys")
        self.passphrase = passphrase
        self.priv_path = self.key_dir / "private.asc"
        self.pub_path = self.key_dir / "public.asc"
        self._ensure_keys()

    # ─── Internal key management ─────────────────────────────────────────
    def _ensure_keys(self) -> None:
        self.key_dir.mkdir(parents=True, exist_ok=True)
        if self.priv_path.exists() and self.pub_path.exists():
            self._load_keys()
            return

        key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
        uid = pgpy.PGPUID.new("swarmauri-user")
        key.add_uid(
            uid,
            usage={KeyFlags.Sign, KeyFlags.EncryptCommunications},
            hashes=[HashAlgorithm.SHA256],
            ciphers=[SymmetricKeyAlgorithm.AES256],
            compression=[CompressionAlgorithm.ZLIB],
        )
        if self.passphrase:
            key.protect(
                self.passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256
            )
        self.private = key
        self.public = key.pubkey
        self.priv_path.write_text(str(self.private))
        self.pub_path.write_text(str(self.public))

    def _load_keys(self) -> None:
        self.private = pgpy.PGPKey()
        self.private.parse(self.priv_path.read_text())
        if self.passphrase:
            self.private.unlock(self.passphrase)
        self.public = pgpy.PGPKey()
        self.public.parse(self.pub_path.read_text())

    # ─── SecretDriveBase / ISecretDrive API ──────────────────────────────
    async def store_key(
        self,
        *,
        key_type: KeyType,
        uses: Iterable[KeyUse],
        name: Optional[str] = None,
        material: Optional[bytes] = None,
        export_policy: ExportPolicy = ExportPolicy.PUBLIC_ONLY,
        tags: Optional[dict[str, str]] = None,
        tenant: Optional[str] = None,
    ) -> KeyDescriptor:
        # For this simple local driver, we only support RSA and opaque material storage.
        if key_type not in (KeyType.RSA, KeyType.OPAQUE, KeyType.SYMMETRIC):
            raise ValueError(f"Unsupported key type: {key_type}")

        # Name determines a subdirectory; if not provided, use fingerprint of generated key
        target_dir = self.key_dir / (name or "default")
        target_dir.mkdir(parents=True, exist_ok=True)

        if material is not None:
            # Treat as opaque or symmetric blob stored as private.asc
            (target_dir / "private.asc").write_bytes(material)
        else:
            # Generate a fresh RSA keypair similar to _ensure_keys
            key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
            uid = pgpy.PGPUID.new(name or "swarmauri-user")
            key.add_uid(
                uid,
                usage={KeyFlags.Sign, KeyFlags.EncryptCommunications},
                hashes=[HashAlgorithm.SHA256],
                ciphers=[SymmetricKeyAlgorithm.AES256],
                compression=[CompressionAlgorithm.ZLIB],
            )
            if self.passphrase:
                key.protect(
                    self.passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256
                )
            (target_dir / "private.asc").write_text(str(key))
            (target_dir / "public.asc").write_text(str(key.pubkey))

        # Construct a minimal KeyDescriptor response
        return KeyDescriptor(
            kid=str(target_dir),
            name=name,
            type=key_type,
            state=KeyState.ENABLED,
            primary_version=1,
            uses=tuple(uses),
            export_policy=export_policy,
            tags=tags or {},
            versions=(
                KeyVersionInfo(version=1, created_at=0.0, state=KeyState.ENABLED),
            ),
        )

    async def load_key(
        self,
        *,
        kid: KeyId,
        version: Optional[KeyVersion] = None,
        require_private: bool = False,
        tenant: Optional[str] = None,
    ) -> KeyRef:
        key_dir = Path(kid)
        pub = key_dir / "public.asc"
        priv = key_dir / "private.asc"
        public_bytes = pub.read_bytes() if pub.exists() else None
        material_bytes = (
            priv.read_bytes() if (require_private and priv.exists()) else None
        )

        return KeyRef(
            kid=str(key_dir),
            version=1,
            type=KeyType.RSA,
            uses=(KeyUse.WRAP, KeyUse.UNWRAP),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            uri=str(key_dir),
            material=material_bytes,
            public=public_bytes,
        )

    async def list(
        self,
        *,
        name_prefix: Optional[str] = None,
        types: Optional[Iterable[KeyType]] = None,
        states: Optional[Iterable[KeyState]] = (KeyState.ENABLED,),
        tags: Optional[dict[str, str]] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> Page:
        items = []
        for sub in self.key_dir.iterdir():
            if not sub.is_dir():
                continue
            if name_prefix and not sub.name.startswith(name_prefix):
                continue
            items.append(
                KeyDescriptor(
                    kid=str(sub),
                    name=sub.name,
                    type=KeyType.RSA,
                    state=KeyState.ENABLED,
                    primary_version=1,
                    uses=(KeyUse.WRAP, KeyUse.UNWRAP),
                    export_policy=ExportPolicy.PUBLIC_ONLY,
                    tags={},
                    versions=(
                        KeyVersionInfo(
                            version=1, created_at=0.0, state=KeyState.ENABLED
                        ),
                    ),
                )
            )
            if len(items) >= limit:
                break
        return Page(items=tuple(items), next_cursor=None)

    async def describe(
        self, *, kid: KeyId, tenant: Optional[str] = None
    ) -> KeyDescriptor:
        sub = Path(kid)
        return KeyDescriptor(
            kid=str(sub),
            name=sub.name,
            type=KeyType.RSA,
            state=KeyState.ENABLED,
            primary_version=1,
            uses=(KeyUse.WRAP, KeyUse.UNWRAP),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            tags={},
            versions=(
                KeyVersionInfo(version=1, created_at=0.0, state=KeyState.ENABLED),
            ),
        )

    async def rotate(
        self,
        *,
        kid: KeyId,
        material: Optional[bytes] = None,
        make_primary: bool = True,
        tags: Optional[dict[str, str]] = None,
        tenant: Optional[str] = None,
    ) -> KeyDescriptor:
        # Simplified: Overwrite private.asc with new material or regenerate
        sub = Path(kid)
        sub.mkdir(parents=True, exist_ok=True)
        if material is not None:
            (sub / "private.asc").write_bytes(material)
        else:
            key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
            uid = pgpy.PGPUID.new(sub.name or "swarmauri-user")
            key.add_uid(
                uid,
                usage={KeyFlags.Sign, KeyFlags.EncryptCommunications},
                hashes=[HashAlgorithm.SHA256],
                ciphers=[SymmetricKeyAlgorithm.AES256],
                compression=[CompressionAlgorithm.ZLIB],
            )
            (sub / "private.asc").write_text(str(key))
            (sub / "public.asc").write_text(str(key.pubkey))

        return await self.describe(kid=kid)

    async def set_state(
        self,
        *,
        kid: KeyId,
        state: KeyState,
        tenant: Optional[str] = None,
    ) -> KeyDescriptor:
        # This simple local driver ignores state changes and returns current description
        return await self.describe(kid=kid)

    # ─── Convenience encryption helpers (ported) ────────────────────────
    def encrypt(self, plaintext: bytes, recipients: Iterable[str]) -> bytes:
        msg = pgpy.PGPMessage.new(plaintext, compression=CompressionAlgorithm.ZLIB)
        sig = self.private.sign(msg)
        msg |= sig
        keys = [self.public]
        for r in recipients:
            k = pgpy.PGPKey()
            try:
                p = Path(r)
                if p.exists():
                    k.parse(p.read_text())
                else:
                    raise OSError
            except OSError:
                k.parse(str(r))
            keys.append(k)
        sessionkey = SymmetricKeyAlgorithm.AES256.gen_key()
        enc_msg = msg
        for k in keys:
            enc_msg = k.encrypt(
                enc_msg,
                cipher=SymmetricKeyAlgorithm.AES256,
                compression=CompressionAlgorithm.ZLIB,
                sessionkey=sessionkey,
            )
        return bytes(str(enc_msg), "utf-8")

    def decrypt(self, ciphertext: bytes) -> bytes:
        enc_msg = pgpy.PGPMessage.from_blob(ciphertext)
        with self.private.unlock(self.passphrase or ""):
            decrypted = self.private.decrypt(enc_msg)
        if not decrypted:
            raise ValueError("decryption failed")
        try:
            verified = self.public.verify(decrypted)
            if not verified:
                raise ValueError
        except Exception:
            pass
        return decrypted.message.encode()

    @staticmethod
    def decrypt_and_verify(
        ciphertext: bytes,
        priv_key: str | Path,
        user_pub: str | Path,
        passphrase: str | None = None,
    ) -> bytes:
        priv = pgpy.PGPKey()
        p = Path(priv_key)
        if isinstance(priv_key, Path) or p.exists():
            priv.parse(p.read_text())
        else:
            priv.parse(str(priv_key))

        if passphrase:
            priv.unlock(passphrase)

        pub = pgpy.PGPKey()
        up = Path(user_pub)
        if isinstance(user_pub, Path) or up.exists():
            pub.parse(up.read_text())
        else:
            pub.parse(str(user_pub))

        message = pgpy.PGPMessage.from_blob(ciphertext)
        decrypted = priv.decrypt(message)
        if not decrypted:
            raise ValueError("decryption failed")
        if not pub.verify(decrypted):
            raise ValueError("signature verification failed")
        return decrypted.message.encode()
