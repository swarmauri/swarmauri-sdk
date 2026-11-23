import pytest

from swarmauri_keyprovider_gcpkms.GcpKmsKeyProvider import _b64d, _b64e


@pytest.mark.perf
def test_b64_roundtrip_perf(benchmark):
    data = b"performance" * 10

    def roundtrip():
        return _b64d(_b64e(data))

    result = benchmark(roundtrip)
    assert result == data
