import pytest
from swarmauri_standard.prompt_samplers.WeightedPromptSampler import WeightedPromptSampler


@pytest.mark.unit
def test_ubc_resource():
    sampler = WeightedPromptSampler()
    assert sampler.resource == "PromptSampler"


@pytest.mark.unit
def test_ubc_type():
    sampler = WeightedPromptSampler()
    assert sampler.type == "WeightedPromptSampler"


@pytest.mark.unit
def test_serialization():
    sampler = WeightedPromptSampler()
    assert sampler.id == WeightedPromptSampler.model_validate_json(sampler.model_dump_json()).id


@pytest.mark.unit
def test_sampling():
    sampler = WeightedPromptSampler()
    prompts = ["a", "b", "c"]
    weights = [0.1, 0.7, 0.2]
    assert sampler.sample(prompts, weights=weights) in prompts
