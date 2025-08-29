from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Literal, Optional
import warnings
from uuid import uuid4

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
from pydantic import PrivateAttr
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

    # Configurable model fields
    # NOTE: `path` is the preferred base directory (if None -> cwd).
    # `key_dir` remains for back-compat; we normalize both to the same base.
    path: Optional[Path] = None
    key_dir: Optional[Path] = None
    passphrase: Optional[str] = None

    # Runtime-only attrs (excluded from serialization)
    _private: pgpy.PGPKey | None = PrivateAttr(default=None)
    _public: pgpy.PGPKey | None = PrivateAttr(default=None)
    _priv_path: Path = PrivateAttr()
    _pub_path: Path = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:  # pydantic v2 hook
        # Resolve base directory precedence: path > key_dir > cwd
        base_dir = self.path or self.key_dir or Path.cwd()
        # Normalize both fields to the resolved base for internal use
        self.path = base_dir
        self.key_dir = base_dir

        self._priv_path = base_dir / "private.asc"
        self._pub_path = base_dir / "public.asc"
        self._ensure_keys()

    @property
    def priv_path(self) -> Path:  # compat for tests/usages
        return self._priv_path

    @property
    def pub_path(self) -> Path:  # compat for tests/usages
        return self._pub_path

    # ─── Internal key management ─────────────────────────────────────────
    def _ensure_keys(self) -> None:
        assert self.key_dir is not None
        self.key_dir.mkdir(parents=True, exist_ok=True)
        if self._priv_path.exists() and self._pub_path.exists():
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
            key.protect(self.passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)
        self._private = key
        self._public = key.pubkey
        self._priv_path.write_text(str(self._private))
        self._pub_path.write_text(str(self._public))

    def _load_keys(self) -> None:
        self._private = pgpy.PGPKey()
        self._private.parse(self._priv_path.read_text())
        # Only unlock on demand in decrypt(); here we keep it locked if passphrase set
        self._public = pgpy.PGPKey()
        self._public.parse(self._pub_path.read_text())

    def _kid_dir(self, kid: str | KeyId) -> Path:
        # Resolve on-disk directory for a given key id (never return the id as a path)
        assert self.key_dir is not None
        return self.key_dir / str(kid)

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
        # Support RSA / OPAQUE / SYMMETRIC in this local driver
        if key_type not in (KeyType.RSA, KeyType.OPAQUE, KeyType.SYMMETRIC):
            raise ValueError(f"Unsupported key type: {key_type}")

        # Choose a stable non-path id: prefer provided name (str) else generate UUID
        kid = name if (name and isinstance(name, str)) else uuid4().hex
        target_dir = self._kid_dir(kid)
        target_dir.mkdir(parents=True, exist_ok=True)

        if material is not None:
            # Treat as opaque or symmetric blob stored as private.asc
            (target_dir / "private.asc").write_bytes(material)
        else:
            # Generate an RSA pair for this kid
            key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
            uid = pgpy.PGPUID.new(name or "swarmauri-user")
            key.add_uid(
                uid,
                usage={KeyFlags.Sign, KeyFlags.EncryptCommunications},
                hashes=[HashAlgorithm.SHA256],
                ciphers=[SymmetricKeyAlgorithm.AES256],
                compression=[CompressionAlgorithm.ZLIB],
            )
            if self.passphrase and key.is_protected is False:
                key.protect(self.passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)
            (target_dir / "private.asc").write_text(str(key))
            (target_dir / "public.asc").write_text(str(key.pubkey))

        return KeyDescriptor(
            kid=kid,                          # <- never a filesystem path
            name=name or kid,
            type=key_type,
            state=KeyState.ENABLED,
            primary_version=1,
            uses=tuple(uses),
            export_policy=export_policy,
            tags=tags or {},
            versions=(KeyVersionInfo(version=1, created_at=0.0, state=KeyState.ENABLED),),
        )

    async def load_key(
        self,
        *,
        kid: KeyId,
        version: Optional[KeyVersion] = None,
        require_private: bool = False,
        tenant: Optional[str] = None,
    ) -> KeyRef:
        d = self._kid_dir(kid)
        pub = d / "public.asc"
        priv = d / "private.asc"
        public_bytes = pub.read_bytes() if pub.exists() else None
        material_bytes = priv.read_bytes() if (require_private and priv.exists()) else None

        return KeyRef(
            kid=str(kid),                     # <- keep as id
            version=1,
            type=KeyType.RSA,
            uses=(KeyUse.WRAP, KeyUse.UNWRAP),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            uri=str(d),                      # <- filesystem location is separate
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
        assert self.key_dir is not None
        items = []
        for sub in self.key_dir.iterdir():
            if not sub.is_dir():
                continue
            kid = sub.name
            if name_prefix and not kid.startswith(name_prefix):
                continue
            items.append(
                KeyDescriptor(
                    kid=kid,
                    name=kid,
                    type=KeyType.RSA,
                    state=KeyState.ENABLED,
                    primary_version=1,
                    uses=(KeyUse.WRAP, KeyUse.UNWRAP),
                    export_policy=ExportPolicy.PUBLIC_ONLY,
                    tags={},
                    versions=(KeyVersionInfo(version=1, created_at=0.0, state=KeyState.ENABLED),),
                )
            )
            if len(items) >= limit:
                break
        return Page(items=tuple(items), next_cursor=None)

    async def describe(self, *, kid: KeyId, tenant: Optional[str] = None) -> KeyDescriptor:
        kid_str = str(kid)
        return KeyDescriptor(
            kid=kid_str,
            name=kid_str,
            type=KeyType.RSA,
            state=KeyState.ENABLED,
            primary_version=1,
            uses=(KeyUse.WRAP, KeyUse.UNWRAP),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            tags={},
            versions=(KeyVersionInfo(version=1, created_at=0.0, state=KeyState.ENABLED),),
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
        d = self._kid_dir(kid)
        d.mkdir(parents=True, exist_ok=True)
        if material is not None:
            (d / "private.asc").write_bytes(material)
        else:
            key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
            uid = pgpy.PGPUID.new(str(kid) or "swarmauri-user")
            key.add_uid(
                uid,
                usage={KeyFlags.Sign, KeyFlags.EncryptCommunications},
                hashes=[HashAlgorithm.SHA256],
                ciphers=[SymmetricKeyAlgorithm.AES256],
                compression=[CompressionAlgorithm.ZLIB],
            )
            (d / "private.asc").write_text(str(key))
            (d / "public.asc").write_text(str(key.pubkey))
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
        # If the private key is protected, sign will require unlock; keep simple here.
        # Users may choose to store the default drive key unprotected or adjust as needed.
        sig = self._private.sign(msg) if self._private else None
        if sig is not None:
            msg |= sig

        keys: list[pgpy.PGPKey] = []
        if self._public:
            keys.append(self._public)

        for r in recipients:
            k = pgpy.PGPKey()
            # Try recipient as a locally stored kid
            local_pub = self._kid_dir(r) / "public.asc"
            try:
                if local_pub.exists():
                    k.parse(local_pub.read_text())
                else:
                    p = Path(r)
                    if p.exists():
                        k.parse(p.read_text())  # treat as file path to armored key
                    else:
                        k.parse(str(r))         # treat as armored key string
                keys.append(k)
            except Exception as e:
                raise ValueError(f"Unable to resolve recipient key '{r}': {e}") from e

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
        if not self._private:
            raise ValueError("private key not loaded")
        with self._private.unlock(self.passphrase or ""):
            decrypted = self._private.decrypt(enc_msg)
        if not decrypted:
            raise ValueError("decryption failed")
        try:
            if self._public and not self._public.verify(decrypted):
                raise ValueError("signature verification failed")
        except Exception:
            # allow unsigned messages
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
