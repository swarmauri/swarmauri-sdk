from auto_kms.orm import Key
from auto_kms.orm import KeyVersion


def test_resource_names():
    assert Key.__resource__ == "key"
    assert KeyVersion.__resource__ == "key_version"
