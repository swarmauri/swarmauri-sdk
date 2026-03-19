from __future__ import annotations

from tigrbl_core._spec.table_registry_spec import TableRegistrySpec


def test_table_registry_spec_defaults_and_values() -> None:
    spec = TableRegistrySpec()
    populated = TableRegistrySpec(tables=("users", "orgs"))

    assert spec.tables == ()
    assert populated.tables == ("users", "orgs")
