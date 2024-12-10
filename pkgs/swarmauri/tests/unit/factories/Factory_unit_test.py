import pytest
from swarmauri.factories.concrete.Factory import Factory
from swarmauri.parsers.concrete.BeautifulSoupElementParser import BeautifulSoupElementParser


def test_factory_register_and_create():
    factory = Factory()

    # Register a resource and type
    factory.register("Parser", "BeautifulSoupElementParser", BeautifulSoupElementParser)

    html_content = "<div><p>Sample HTML content</p></div>"

    # Create an instance
    instance = factory.create("Parser", "BeautifulSoupElementParser", element=html_content)
    assert isinstance(instance, BeautifulSoupElementParser)
    assert instance.type == "BeautifulSoupElementParser"


def test_factory_duplicate_register():
    factory = Factory()
    factory.register("Parser", "BeautifulSoupElementParser", BeautifulSoupElementParser)

    # Attempt to register the same type again
    with pytest.raises(
        ValueError,
        match="Type 'BeautifulSoupElementParser' is already registered under resource 'Parser'.",
    ):
        factory.register("Parser", "BeautifulSoupElementParser", BeautifulSoupElementParser)


def test_factory_create_unregistered_resource():
    factory = Factory()

    # Attempt to create an instance of an unregistered resource
    with pytest.raises(
        ValueError, match="Resource 'UnknownResource' is not registered."
    ):
        factory.create("UnknownResource", "BeautifulSoupElementParser")


def test_factory_create_unregistered_type():
    factory = Factory()
    factory.register("Parser", "BeautifulSoupElementParser", BeautifulSoupElementParser)

    # Attempt to create an instance of an unregistered type
    with pytest.raises(
        ValueError,
        match="Type 'UnknownType' is not registered under resource 'Parser'.",
    ):
        factory.create("Parser", "UnknownType")
