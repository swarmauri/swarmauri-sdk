from swarmauri_base import GitFilterBase
from swarmauri_gitfilter_minio import MinioFilter


def test_inherits_base():
    assert issubclass(MinioFilter, GitFilterBase)
