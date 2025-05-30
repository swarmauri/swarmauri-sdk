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
    sampler = PromptSampler(prompts=["a"])
    assert sampler.id == PromptSampler.model_validate_json(sampler.model_dump_json()).id


@pytest.mark.unit
def test_sampling_with_argument():
    sampler = PromptSampler()
    prompts = ["a", "b", "c"]
    assert sampler.sample(prompts) in prompts


@pytest.mark.unit
def test_sampling_from_attribute():
    sampler = PromptSampler(prompts=["a", "b", "c"])
    assert sampler.sample() in ["a", "b", "c"]


@pytest.mark.unit
def test_manipulation_methods():
    sampler = PromptSampler(prompts=["a"])
    sampler.add_prompt("b")
    sampler.add_prompts(["c", "d"])
    assert sampler.show() == ["a", "b", "c", "d"]
    sampler.remove_prompt("c")
    assert sampler.show() == ["a", "b", "d"]
    sampler.clear_prompts()
    assert sampler.show() == []
