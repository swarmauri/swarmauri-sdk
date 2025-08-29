from auto_kms.tables.key import Key
from auto_kms.tables.key_version import KeyVersion


def test_resource_names():
    assert Key.__resource__ == "key"
    assert KeyVersion.__resource__ == "key_version"
