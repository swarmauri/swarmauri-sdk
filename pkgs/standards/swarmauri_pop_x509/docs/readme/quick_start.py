import asyncio
import ssl
from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy, BindType
from swarmauri_pop_x509 import X509PoPVerifier


async def main() -> None:
    verifier = X509PoPVerifier()
    cnf = CnfBinding(BindType.X5T_S256, "<thumbprint-from-token>")
    request = HttpParts(
        method="GET", url="https://api.example.com/resource", headers={}
    )

    peer_cert_der = ssl.PEM_cert_to_DER_cert(
        open("client.pem", "r", encoding="utf-8").read()
    )

    await verifier.verify_http(
        request,
        cnf,
        policy=VerifyPolicy(),
        extras={"peer_cert_der": peer_cert_der},
    )


asyncio.run(main())
