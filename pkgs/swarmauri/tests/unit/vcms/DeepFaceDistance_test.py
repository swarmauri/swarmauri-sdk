import pytest
from swarmauri.vcms.concrete.DeepFaceDistance import DeepFaceDistance


@pytest.mark.unit
def test_ubc_resource():
    assert DeepFaceDistance().resource == "VCM"


@pytest.mark.unit
def test_ubc_type():
    assert DeepFaceDistance().type == "DeepFaceDistance"


@pytest.mark.unit
def test_serialization():
    dfd = DeepFaceDistance()
    assert dfd.id == DeepFaceDistance.model_validate_json(dfd.model_dump_json()).id


@pytest.mark.unit
def test_default_name():
    assert DeepFaceDistance().name == "VGG-Face"


