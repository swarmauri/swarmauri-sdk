import pytest
from swarmauri_standard.prompt_samplers.SequentialPromptSampler import SequentialPromptSampler


@pytest.mark.unit
def test_ubc_resource():
    sampler = SequentialPromptSampler()
    assert sampler.resource == "PromptSampler"


@pytest.mark.unit
def test_ubc_type():
    sampler = SequentialPromptSampler()
    assert sampler.type == "SequentialPromptSampler"


@pytest.mark.unit
def test_serialization():
    sampler = SequentialPromptSampler()
    assert sampler.id == SequentialPromptSampler.model_validate_json(sampler.model_dump_json()).id


@pytest.mark.unit
def test_sampling_sequential():
    sampler = SequentialPromptSampler()
    prompts = ["a", "b", "c"]
    assert sampler.sample(prompts) == "a"
    assert sampler.sample(prompts) == "b"
    assert sampler.sample(prompts) == "c"
    assert sampler.sample(prompts) == "a"
