from autoapi.v3.types.op_config_provider import should_wire_canonical
from autoapi.v3.mixins import BulkCapable, Replaceable

DEFAULT_VERBS = {
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
}


def test_should_wire_canonical_defaults():
    class Plain:
        pass

    for verb in DEFAULT_VERBS:
        assert should_wire_canonical(Plain, verb)


def test_should_wire_canonical_bulkcapable():
    class Bulk(BulkCapable):
        pass

    for verb in DEFAULT_VERBS:
        assert should_wire_canonical(Bulk, verb)


def test_should_wire_canonical_replaceable():
    class Rep(Replaceable):
        pass

    for verb in DEFAULT_VERBS:
        assert should_wire_canonical(Rep, verb)


def test_should_wire_canonical_bulk_and_replace():
    class Both(BulkCapable, Replaceable):
        pass

    for verb in DEFAULT_VERBS:
        assert should_wire_canonical(Both, verb)
