import pytest
from swarmauri.vcms.concrete.DeepFaceEmbedder import DeepFaceEmbedder


@pytest.mark.unit
def test_ubc_resource():
    assert DeepFaceEmbedder().resource == "VCM"


@pytest.mark.unit
def test_ubc_type():
    assert DeepFaceEmbedder().type == "DeepFaceEmbedder"


@pytest.mark.unit
def test_serialization():
    dfe = DeepFaceEmbedder()
    assert dfe.id == DeepFaceEmbedder.model_validate_json(dfe.model_dump_json()).id


@pytest.mark.unit
def test_default_name():
    assert DeepFaceEmbedder().name == "VGG-Face"


