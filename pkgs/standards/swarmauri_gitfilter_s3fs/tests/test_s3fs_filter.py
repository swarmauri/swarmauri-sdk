from swarmauri_base import GitFilterBase
from swarmauri_gitfilter_s3fs import S3FSFilter


def test_inherits_base():
    assert issubclass(S3FSFilter, GitFilterBase)
