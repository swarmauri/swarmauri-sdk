import asyncio
import pytest

from swarmauri_certs_crlverifyservice import CrlVerifyService


@pytest.mark.perf
def test_verify_cert_perf(cert_and_crl, benchmark) -> None:
    cert, crls = cert_and_crl()
    svc = CrlVerifyService()

    def run():
        return asyncio.run(svc.verify_cert(cert, crls=crls))

    result = benchmark(run)
    assert result["valid"] is True
