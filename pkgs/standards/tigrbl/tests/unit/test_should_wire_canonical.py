from tigrbl.orm.mixins import BulkCapable, Mergeable, Replaceable
from tigrbl.op.canonical import should_wire_canonical

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
    for verb in BULK_VERBS | {"merge"}:
        assert not should_wire_canonical(Plain, verb)


def test_should_wire_canonical_bulkcapable():
    class Bulk(BulkCapable):
        pass

    for verb in NON_BULK_VERBS | {"bulk_create", "bulk_update", "bulk_delete"}:
        assert should_wire_canonical(Bulk, verb)
    for verb in {"bulk_replace", "merge", "bulk_merge"}:
        assert not should_wire_canonical(Bulk, verb)


def test_should_wire_canonical_replaceable():
    class Rep(Replaceable):
        pass

    for verb in NON_BULK_VERBS:
        assert should_wire_canonical(Rep, verb)
    assert should_wire_canonical(Rep, "bulk_replace")
    for verb in {"bulk_create", "bulk_update", "bulk_merge", "bulk_delete", "merge"}:
        assert not should_wire_canonical(Rep, verb)


def test_should_wire_canonical_mergeable():
    class Merge(Mergeable):
        pass

    for verb in NON_BULK_VERBS | {"merge"}:
        assert should_wire_canonical(Merge, verb)
    assert should_wire_canonical(Merge, "bulk_merge")
    for verb in {"bulk_create", "bulk_update", "bulk_replace", "bulk_delete"}:
        assert not should_wire_canonical(Merge, verb)
