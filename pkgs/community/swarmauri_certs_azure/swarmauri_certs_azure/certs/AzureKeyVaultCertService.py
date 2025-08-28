from __future__ import annotations

import base64
import datetime as dt
import random
from typing import Any, Dict, Iterable, Literal, Mapping, Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import AltNameSpec, SubjectSpec
from swarmauri_core.crypto.types import KeyRef


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_utc() -> dt.datetime:
    """Return current UTC time."""
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)


def _serial_or_random(serial: Optional[int]) -> int:
    """Return provided serial number or a random 128-bit value per RFC 5280."""
    if serial is not None:
        return int(serial)
    return random.SystemRandom().getrandbits(128)


def _pem_cert(der_bytes: bytes) -> bytes:
    """Encode DER certificate bytes into PEM as described in RFC 7468."""
    b64 = base64.encodebytes(der_bytes).decode("ascii").replace("\n", "")
    lines = [b64[i : i + 64] for i in range(0, len(b64), 64)]
    return (
        "-----BEGIN CERTIFICATE-----\n"
        + "\n".join(lines)
        + "\n-----END CERTIFICATE-----\n"
    ).encode("ascii")


def _to_x509_name(spec: SubjectSpec) -> x509.Name:
    rdns = []
    if cn := spec.get("CN"):
        rdns.append(x509.NameAttribute(NameOID.COMMON_NAME, cn))
    return x509.Name(rdns)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class AzureKeyVaultCertService(CertServiceBase):
    """Minimal Azure Key Vault backed certificate service."""

    type: Literal["AzureKeyVaultCertService"] = "AzureKeyVaultCertService"

    def __init__(self, vault_url: str, *, credential: Optional[Any] = None) -> None:
        super().__init__()
        self._cred = credential or DefaultAzureCredential()
        self._keys = KeyClient(vault_url=vault_url, credential=self._cred)

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048",),
            "sig_algs": ("RSA-SHA256",),
            "features": ("csr",),
        }

    async def create_csr(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        san: Optional[AltNameSpec] = None,
        extensions: Optional[Dict[str, Any]] = None,
        sig_alg: Optional[str] = None,
        challenge_password: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Create a PKCS#10 CSR using the supplied key material."""
        pem_priv = key.material
        if not pem_priv:
            raise NotImplementedError(
                "Non-exportable keys are not supported in this simplified service."
            )
        subject_name = _to_x509_name(subject)
        builder = x509.CertificateSigningRequestBuilder().subject_name(subject_name)
        priv = serialization.load_pem_private_key(pem_priv, password=None)
        csr = builder.sign(priv, hashes.SHA256())
        encoding = (
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )
        return csr.public_bytes(encoding)
