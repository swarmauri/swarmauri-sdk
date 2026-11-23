import pytest

from swarmauri_standard.evaluator_pools.EvaluatorPool import EvaluatorPool


@pytest.mark.unit
def test_resource_type():
    pool = EvaluatorPool()
    assert pool.resource == "EvaluatorPool"


@pytest.mark.unit
def test_type_literal():
    pool = EvaluatorPool()
    assert pool.type == "EvaluatorPool"


@pytest.mark.unit
def test_serialization_roundtrip():
    pool = EvaluatorPool()
    dumped = pool.model_dump_json()
    loaded = EvaluatorPool.model_validate_json(dumped)
    assert isinstance(loaded, EvaluatorPool)
