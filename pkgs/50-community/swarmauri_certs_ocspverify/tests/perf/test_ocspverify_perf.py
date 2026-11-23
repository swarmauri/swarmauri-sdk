import pytest

from swarmauri_certs_ocspverify import OcspVerifyService


@pytest.mark.perf
def test_supports_perf(benchmark) -> None:
    svc = OcspVerifyService()
    result = benchmark(svc.supports)
    assert "ocsp" in result["features"]
