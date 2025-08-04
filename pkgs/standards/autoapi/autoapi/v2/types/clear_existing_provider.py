from .table_config_provider import TableConfigProvider


class ClearExistingTableProvider(TableConfigProvider):
    """Marker for tables that should be cleared on API startup."""

    pass


__all__ = ["ClearExistingTableProvider"]
