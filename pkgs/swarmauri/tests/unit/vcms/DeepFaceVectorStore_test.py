import pytest
from swarmauri.vcms.concrete.DeepFaceVectorStore import DeepFaceVectorStore


@pytest.mark.unit
def test_ubc_resource():
    assert DeepFaceVectorStore().resource == "VCM"


@pytest.mark.unit
def test_ubc_type():
    assert DeepFaceVectorStore().type == "DeepFaceVectorStore"


@pytest.mark.unit
def test_serialization():
    dfvs = DeepFaceVectorStore()
    assert dfvs.id == DeepFaceVectorStore.model_validate_json(dfvs.model_dump_json()).id


@pytest.mark.unit
def test_default_name():
    assert DeepFaceVectorStore().name == "VGG-Face"


