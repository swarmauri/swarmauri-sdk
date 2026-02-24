import pytest

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider
from swarmauri_core.key_providers.types import KeyAlg


@pytest.mark.unit
def test_supports_includes_rsa():
    provider = AwsKmsKeyProvider(region="us-east-1")
    assert KeyAlg.RSA_OAEP_SHA256 in provider.supports()["algs"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_random_bytes_length():
    provider = AwsKmsKeyProvider(region="us-east-1")
    data = await provider.random_bytes(32)
    assert len(data) == 32
