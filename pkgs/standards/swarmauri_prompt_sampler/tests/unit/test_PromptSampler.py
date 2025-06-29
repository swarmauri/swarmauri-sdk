import pytest
from swarmauri_prompt_sampler.PromptSampler import PromptSampler


@pytest.mark.unit
def test_type_and_resource():
    sampler = PromptSampler(prompts=["a", "b"])
    assert sampler.type == "PromptSampler"
    assert sampler.resource == "Prompt"


@pytest.mark.unit
def test_sample_single():
    sampler = PromptSampler(prompts=["a", "b"])
    result = sampler.sample()
    assert len(result) == 1
    assert result[0] in ["a", "b"]


@pytest.mark.unit
def test_sample_multiple():
    sampler = PromptSampler(prompts=["a", "b", "c"])
    results = sampler.sample(2)
    assert len(results) == 2
    for r in results:
        assert r in ["a", "b", "c"]
