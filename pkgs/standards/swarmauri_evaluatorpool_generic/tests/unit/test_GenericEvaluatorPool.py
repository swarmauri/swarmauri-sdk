import pytest
from swarmauri_evaluatorpool_generic.GenericEvaluatorPool import GenericEvaluatorPool


@pytest.mark.unit
def test_resource():
    assert GenericEvaluatorPool().resource == "EvaluatorPool"


@pytest.mark.unit
def test_type():
    assert GenericEvaluatorPool().type == "GenericEvaluatorPool"


@pytest.mark.unit
def test_serialization_roundtrip():
    pool = GenericEvaluatorPool()
    dumped = pool.model_dump_json()
    loaded = GenericEvaluatorPool.model_validate_json(dumped)
    assert pool.id == loaded.id
