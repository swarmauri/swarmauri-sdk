"""Lesson 09.2: Registering table configuration providers."""

from tigrbl.types import TableConfigProvider
from tigrbl.types.table_config_provider import list_table_config_providers


def test_table_config_providers_register():
    """Explain how subclassing registers a provider globally.

    Purpose: verify that table config providers auto-register on subclassing.
    Design practice: create small provider classes to keep config modular.
    """

    # Setup: define a provider subclass to trigger registration.
    class LessonProvider(TableConfigProvider):
        pass

    # Test: request the provider list from the registry.
    providers = list_table_config_providers()

    # Assertion: the new provider is discoverable by name.
    assert any(provider.__name__ == "LessonProvider" for provider in providers)


def test_table_config_providers_are_sorted_by_name():
    """Show that provider listing is deterministic.

    Purpose: confirm that list helpers return providers in name order for
    stable debugging and documentation output.
    Design practice: rely on deterministic ordering when presenting config.
    """

    # Setup: define multiple providers to populate the registry.
    class AlphaProvider(TableConfigProvider):
        pass

    class ZetaProvider(TableConfigProvider):
        pass

    # Test: gather provider names in list order.
    providers = list_table_config_providers()
    names = [provider.__name__ for provider in providers]

    # Assertion: providers are returned in deterministic name order.
    assert names == sorted(names)
