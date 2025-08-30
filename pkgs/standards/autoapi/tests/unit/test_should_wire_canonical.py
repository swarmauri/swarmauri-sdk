from autoapi.v3.mixins import BulkCapable, Replaceable
from autoapi.v3.opspec.canonical import should_wire_canonical

NON_BULK_VERBS = {
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
}

BULK_VERBS = {
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
}


def test_should_wire_canonical_defaults():
    class Plain:
        pass

    for verb in NON_BULK_VERBS:
        assert should_wire_canonical(Plain, verb)
    for verb in BULK_VERBS:
        assert not should_wire_canonical(Plain, verb)


def test_should_wire_canonical_bulkcapable():
    class Bulk(BulkCapable):
        pass

    for verb in (NON_BULK_VERBS - {"merge"}) | {
        "bulk_create",
        "bulk_update",
        "bulk_delete",
    }:
        assert should_wire_canonical(Bulk, verb)
    assert not should_wire_canonical(Bulk, "bulk_replace")
    assert not should_wire_canonical(Bulk, "merge")
    assert not should_wire_canonical(Bulk, "bulk_merge")


def test_should_wire_canonical_replaceable():
    class Rep(Replaceable):
        pass

    for verb in NON_BULK_VERBS:
        assert should_wire_canonical(Rep, verb)
    assert should_wire_canonical(Rep, "bulk_replace")
    for verb in {"bulk_create", "bulk_update", "bulk_merge", "bulk_delete"}:
        assert not should_wire_canonical(Rep, verb)


def test_should_wire_canonical_bulk_and_replace():
    class Both(BulkCapable, Replaceable):
        pass

    for verb in (NON_BULK_VERBS | BULK_VERBS) - {"merge", "bulk_merge"}:
        assert should_wire_canonical(Both, verb)
    assert not should_wire_canonical(Both, "merge")
    assert not should_wire_canonical(Both, "bulk_merge")
