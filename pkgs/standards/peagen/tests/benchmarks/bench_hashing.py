import pytest

from peagen.utils.hashing import payload_hash


@pytest.mark.perf
def test_payload_hash_benchmark(benchmark):
    data = {"foo": "bar"}
    benchmark(lambda: payload_hash(data))
