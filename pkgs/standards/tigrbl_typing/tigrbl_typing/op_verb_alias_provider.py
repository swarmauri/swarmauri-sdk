from typing import Callable, ClassVar, Mapping, Literal

from .table_config_provider import TableConfigProvider

_VERB_ALIAS_PROVIDERS: set[type] = set()


class OpVerbAliasProvider(TableConfigProvider):
    """
    Table-level config provider to rename operation verbs for RPC exposure.
    Does not change REST routes or internal canonical semantics.
    """

    # Map canonical → alias (e.g., {"create": "register"})
    __tigrbl_verb_aliases__: ClassVar[
        Mapping[str, str] | Callable[[], Mapping[str, str]]
    ] = {}

    # How to expose names:
    #  - "both" (default): expose canonical & alias
    #  - "alias_only": expose alias only
    #  - "canonical_only": ignore aliases, keep canonical only
    __tigrbl_verb_alias_policy__: ClassVar[
        Literal["both", "alias_only", "canonical_only"]
    ] = "both"

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _VERB_ALIAS_PROVIDERS.add(cls)


def list_verb_alias_providers():
    return sorted(_VERB_ALIAS_PROVIDERS, key=lambda c: c.__name__)
