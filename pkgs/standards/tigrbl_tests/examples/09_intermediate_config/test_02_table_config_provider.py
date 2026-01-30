from tigrbl.types import TableConfigProvider
from tigrbl.types.table_config_provider import list_table_config_providers


def test_table_config_providers_register():
    class LessonProvider(TableConfigProvider):
        pass

    providers = list_table_config_providers()
    assert any(provider.__name__ == "LessonProvider" for provider in providers)
