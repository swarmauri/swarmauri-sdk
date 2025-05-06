import pytest
from swarmauri_standard.factories.Factory import Factory
from swarmauri_standard.parsers.HTMLTagStripParser import (
    HTMLTagStripParser,
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
def test_factory_register_create_resource(factory):
    # Register a resource and type
    factory.register("Parser", "HTMLTagStripParser", HTMLTagStripParser)

    html_content = "<div><p>Sample HTML content</p></div>"

    # Create an instance
    instance = factory.create("Parser", "HTMLTagStripParser", element=html_content)
    assert isinstance(instance, HTMLTagStripParser)
    assert instance.type == "HTMLTagStripParser"


@pytest.mark.unit
def test_factory_create_unregistered_resource(factory):
    # Attempt to create an instance of an unregistered resource
    with pytest.raises(
        ModuleNotFoundError, match="Resource 'UnknownResource' is not registered."
    ):
        factory.create("UnknownResource", "HTMLTagStripParser")


@pytest.mark.unit
def test_factory_duplicate_register(factory):
    # Attempt to register the same type again
    with pytest.raises(
        ValueError,
        match="Type 'HTMLTagStripParser' is already registered under resource 'Parser'.",
    ):
        factory.register("Parser", "HTMLTagStripParser", HTMLTagStripParser)


@pytest.mark.unit
def test_factory_create_unregistered_type(factory):
    # Attempt to create an instance of an unregistered type
    with pytest.raises(
        ValueError,
        match="Type 'UnknownType' is not registered under resource 'Parser'.",
    ):
        factory.create("Parser", "UnknownType")
