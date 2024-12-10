import pytest
from swarmauri.factories.concrete.AgentFactory import AgentFactory

class MockParser:
    def __init__(self, name: str):
        self.name = name


def test_agent_factory_register_and_create():
    factory = AgentFactory()

    # Register a resource
    factory.register("MockParser", MockParser)

    # Create an instance
    instance = factory.create("MockParser", name="TestParser")
    assert isinstance(instance, MockParser)
    assert instance.name == "TestParser"


def test_agent_factory_duplicate_register():
    factory = AgentFactory()
    factory.register("MockParser", MockParser)

    # Attempt to register the same type again
    with pytest.raises(ValueError, match="Type 'MockParser' is already registered."):
        factory.register("MockParser", MockParser)


def test_agent_factory_create_unregistered_type():
    factory = AgentFactory()

    # Attempt to create an unregistered type
    with pytest.raises(ValueError, match="Type 'UnregisteredType' is not registered."):
        factory.create("UnregisteredType")
