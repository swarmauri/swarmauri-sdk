import pytest
from swarmauri_standard.prompt_samplers.PromptSampler import PromptSampler


@pytest.mark.unit
def test_ubc_resource():
    sampler = PromptSampler()
    assert sampler.resource == "PromptSampler"


@pytest.mark.unit
def test_ubc_type():
    sampler = PromptSampler()
    assert sampler.type == "PromptSampler"


@pytest.mark.unit
def test_serialization():
    sampler = PromptSampler()
    assert sampler.id == PromptSampler.model_validate_json(sampler.model_dump_json()).id


@pytest.mark.unit
def test_sampling():
    sampler = PromptSampler()
    prompts = ["a", "b", "c"]
    assert sampler.sample(prompts) in prompts
