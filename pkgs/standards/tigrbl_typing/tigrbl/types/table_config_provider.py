_TABLE_CONFIG_PROVIDERS: set[type] = set()


class TableConfigProvider:
    """Marker base for table-level configuration providers."""

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _TABLE_CONFIG_PROVIDERS.add(cls)


def list_table_config_providers():
    return sorted(_TABLE_CONFIG_PROVIDERS, key=lambda c: c.__name__)
