import asyncio

import pytest

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider


@pytest.mark.perf
def test_random_bytes_perf(benchmark):
    provider = AwsKmsKeyProvider(region="us-east-1")

    def run():
        return asyncio.run(provider.random_bytes(64))

    result = benchmark(run)
    assert len(result) == 64
