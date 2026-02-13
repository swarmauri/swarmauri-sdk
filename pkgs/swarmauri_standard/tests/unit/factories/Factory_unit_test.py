import importlib

import pytest
from swarmauri_standard.factories.Factory import Factory
from swarmauri_standard.parsers.HTMLTagStripParser import HTMLTagStripParser


class _GreetingParser:
    def __init__(self, prefix: str, *, suffix: str = ""):
        self.prefix = prefix
        self.suffix = suffix


class _CounterParser:
    def __init__(self, start: int = 0):
        self.start = start


@pytest.fixture(autouse=True)
def reset_factory_registry():
    Factory._resource_registry = {}


@pytest.fixture
def factory():
    return Factory()


@pytest.mark.unit
def test_ubc_resource(factory):
    assert factory.resource == "Factory"


@pytest.mark.unit
def test_factory_import_path_resolves_factory_class():
    module = importlib.import_module("swarmauri_standard.factories.Factory")
    assert module.Factory is Factory


@pytest.mark.unit
def test_ubc_type(factory):
    assert factory.type == "Factory"


@pytest.mark.unit
def test_serialization(factory):
    assert factory.id == Factory.model_validate_json(factory.model_dump_json()).id


@pytest.mark.unit
def test_factory_register_create_resource(factory):
    factory.register("Parser", "HTMLTagStripParser", HTMLTagStripParser)

    html_content = "<div><p>Sample HTML content</p></div>"
    instance = factory.create("Parser", "HTMLTagStripParser", element=html_content)

    assert isinstance(instance, HTMLTagStripParser)
    assert instance.type == "HTMLTagStripParser"


@pytest.mark.unit
def test_factory_create_unregistered_resource(factory):
    with pytest.raises(
        ModuleNotFoundError, match="Resource 'UnknownResource' is not registered."
    ):
        factory.create("UnknownResource", "HTMLTagStripParser")


@pytest.mark.unit
def test_factory_duplicate_register(factory):
    factory.register("Parser", "HTMLTagStripParser", HTMLTagStripParser)
    with pytest.raises(
        ValueError,
        match="Type 'HTMLTagStripParser' is already registered under resource 'Parser'.",
    ):
        factory.register("Parser", "HTMLTagStripParser", HTMLTagStripParser)


@pytest.mark.unit
def test_factory_create_unregistered_type(factory):
    factory.register("Parser", "HTMLTagStripParser", HTMLTagStripParser)
    with pytest.raises(
        ValueError,
        match="Type 'UnknownType' is not registered under resource 'Parser'.",
    ):
        factory.create("Parser", "UnknownType")


@pytest.mark.unit
def test_factory_create_passes_positional_and_keyword_arguments(factory):
    factory.register("Parser", "GreetingParser", _GreetingParser)

    instance = factory.create("Parser", "GreetingParser", "hello", suffix="!")

    assert isinstance(instance, _GreetingParser)
    assert instance.prefix == "hello"
    assert instance.suffix == "!"


@pytest.mark.unit
def test_factory_can_register_and_create_multiple_types_for_one_resource(factory):
    factory.register("Parser", "GreetingParser", _GreetingParser)
    factory.register("Parser", "CounterParser", _CounterParser)

    greeting = factory.create("Parser", "GreetingParser", "hola", suffix="?")
    counter = factory.create("Parser", "CounterParser", start=4)

    assert isinstance(greeting, _GreetingParser)
    assert greeting.prefix == "hola"
    assert greeting.suffix == "?"
    assert isinstance(counter, _CounterParser)
    assert counter.start == 4


@pytest.mark.unit
def test_factory_registered_type_can_be_created_from_another_instance():
    first_factory = Factory()
    second_factory = Factory()

    first_factory.register("Parser", "GreetingParser", _GreetingParser)
    created = second_factory.create("Parser", "GreetingParser", "shared")

    assert isinstance(created, _GreetingParser)
    assert created.prefix == "shared"
