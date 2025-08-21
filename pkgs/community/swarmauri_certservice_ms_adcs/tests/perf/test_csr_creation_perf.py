import asyncio
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from swarmauri_core.certs.ICertService import SubjectSpec


def _make_key() -> KeyRef:
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="k1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        material=pem,
    )


def test_csr_creation_perf(benchmark) -> None:
    key = _make_key()
    svc = MsAdcsCertService(base_url="https://example.com", auth=_AuthCfg(mode="none"))
    subject: SubjectSpec = {"CN": "perf"}

    async def _run() -> None:
        await svc.create_csr(key, subject)

    benchmark(lambda: asyncio.run(_run()))
