from types import SimpleNamespace

from tigrbl.mapping.column_mro_collect import mro_collect_columns


def test_mro_collect_columns_accepts_namespace_columns() -> None:
    class NamespaceColumnsModel:
        columns = SimpleNamespace(
            alpha=SimpleNamespace(name="alpha"),
            beta=SimpleNamespace(name="beta"),
        )

    cols = mro_collect_columns(NamespaceColumnsModel)

    assert sorted(cols.keys()) == ["alpha", "beta"]
