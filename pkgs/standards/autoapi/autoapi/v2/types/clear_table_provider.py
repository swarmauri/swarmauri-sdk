from .table_config_provider import TableConfigProvider

_CLEAR_TABLE_PROVIDERS: set[type] = set()


class ClearTableProvider(TableConfigProvider):
    """Models that should be cleared on AutoAPI initialization."""

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _CLEAR_TABLE_PROVIDERS.add(cls)


def list_clear_table_providers():
    return sorted(_CLEAR_TABLE_PROVIDERS, key=lambda c: c.__name__)
