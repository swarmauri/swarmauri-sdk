import pytest
from swarmauri_prompt_template_sampler.PromptTemplateSampler import PromptTemplateSampler


@pytest.mark.unit
def test_type_and_resource():
    pts = PromptTemplateSampler(templates=["Hello {name}"])
    assert pts.type == "PromptTemplateSampler"
    assert pts.resource == "Prompt"


@pytest.mark.unit
def test_sample_renders_variables():
    pts = PromptTemplateSampler(templates=["Hello {name}"])
    result = pts.sample({"name": "World"})
    assert result == "Hello World"
