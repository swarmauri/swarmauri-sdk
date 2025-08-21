"""Performance tests for CfsslCertService."""

import asyncio

import pytest

from swarmauri_cert_cfssl import CfsslCertService


@pytest.mark.perf
def test_parse_perf(benchmark, cert_pem: bytes) -> None:
    """Benchmark certificate parsing."""
    svc = CfsslCertService(base_url="https://cfssl.example")

    def run() -> None:
        asyncio.run(svc.parse_cert(cert_pem))

    benchmark(run)
