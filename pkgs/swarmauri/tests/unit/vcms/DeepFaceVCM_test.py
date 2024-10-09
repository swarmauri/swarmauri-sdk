import pytest
from swarmauri.vcms.concrete.DeepFaceVCM import DeepFaceVCM


@pytest.mark.unit
def test_ubc_resource():
    assert DeepFaceVCM().resource == "VCM"


@pytest.mark.unit
def test_ubc_type():
    assert DeepFaceVCM().type == "DeepFaceVCM"


@pytest.mark.unit
def test_serialization():
    dfvcm = DeepFaceVCM()
    assert dfvcm.id == DeepFaceVCM.model_validate_json(dfvcm.model_dump_json()).id



