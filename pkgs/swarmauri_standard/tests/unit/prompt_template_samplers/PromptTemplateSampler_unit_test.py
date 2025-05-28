import pytest

from swarmauri_standard.prompt_template_samplers.PromptTemplateSampler import PromptTemplateSampler
from swarmauri_standard.prompt_templates.PromptTemplate import PromptTemplate


@pytest.mark.unit
def test_resource_value():
    sampler = PromptTemplateSampler(templates=[PromptTemplate(template="hi")])
    assert sampler.resource == "PromptTemplateSampler"


@pytest.mark.unit
def test_type_literal():
    sampler = PromptTemplateSampler()
    assert sampler.type == "PromptTemplateSampler"


@pytest.mark.unit
def test_serialization_roundtrip():
    sampler = PromptTemplateSampler()
    dumped = sampler.model_dump_json()
    loaded = PromptTemplateSampler.model_validate_json(dumped)
    assert isinstance(loaded, PromptTemplateSampler)


@pytest.mark.unit
def test_sample_returns_template():
    tmpl1 = PromptTemplate(template="a")
    tmpl2 = PromptTemplate(template="b")
    sampler = PromptTemplateSampler(templates=[tmpl1, tmpl2])
    assert sampler.sample() in [tmpl1, tmpl2]


@pytest.mark.unit
def test_template_manipulation_methods():
    tmpl1 = PromptTemplate(template="1")
    tmpl2 = PromptTemplate(template="2")
    sampler = PromptTemplateSampler()

    sampler.add_template(tmpl1)
    sampler.add_templates([tmpl2])
    assert sampler.templates == [tmpl1, tmpl2]

    sampler.remove_template(0)
    assert sampler.templates == [tmpl2]

    sampler.clear_templates()
    assert sampler.templates == []

