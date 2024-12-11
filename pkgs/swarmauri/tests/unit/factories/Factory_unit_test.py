import pytest
from swarmauri.factories.concrete.Factory import Factory
from swarmauri.parsers.concrete.BeautifulSoupElementParser import (
    BeautifulSoupElementParser,
)


@pytest.fixture(scope="module")
def factory():
    return Factory()


@pytest.mark.unit
def test_ubc_resource(factory):
    assert factory.resource == "Factory"


@pytest.mark.unit
def test_ubc_type(factory):
    assert factory.type == "Factory"


@pytest.mark.unit
def test_serialization(factory):
    assert factory.id == Factory.model_validate_json(factory.model_dump_json()).id


@pytest.mark.unit
def test_factory_create(factory):

    html_content = "<div><p>Sample HTML content</p></div>"

    # Create an instance
    instance = factory.create(
        "Parser", "BeautifulSoupElementParser", element=html_content
    )
    assert isinstance(instance, BeautifulSoupElementParser)
    assert instance.type == "BeautifulSoupElementParser"


@pytest.mark.unit
def test_factory_create_unregistered_resource(factory):

    # Attempt to create an instance of an unregistered resource
    with pytest.raises(
        ModuleNotFoundError, match="Resource 'UnknownResource' is not found."
    ):
        factory.create("UnknownResource", "BeautifulSoupElementParser")


@pytest.mark.unit
def test_factory_create_unregistered_type(factory):

    # Attempt to create an instance of an unregistered type
    with pytest.raises(
        ValueError,
        match="Type 'UnknownType' does not exist under resource 'Parser'.",
    ):
        factory.create("Parser", "UnknownType")
