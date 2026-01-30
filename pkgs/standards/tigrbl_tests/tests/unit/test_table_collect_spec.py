from tigrbl.table.mro_collect import mro_collect_table_spec
from tigrbl.table.shortcuts import defineTableSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk


SpecA = defineTableSpec(
    engine="db_a",
    ops=["a"],
    columns=["col_a"],
    schemas=["SchemaA"],
    hooks=["hook_a"],
    security_deps=["sec_a"],
    deps=["dep_a"],
)

SpecB = defineTableSpec(
    engine="db_b",
    ops=["b"],
    columns=["col_b"],
    schemas=["SchemaB"],
    hooks=["hook_b"],
    security_deps=["sec_b"],
    deps=["dep_b"],
)


class Model(SpecA, SpecB, Base, GUIDPk):
    __tablename__ = "collect_spec_model"


def test_collect_table_spec_merges_mro():
    spec = mro_collect_table_spec(Model)
    assert spec.model is Model
    assert spec.engine == "db_a"
    assert spec.ops == ("a", "b")
    assert spec.columns == ("col_a", "col_b")
    assert spec.schemas == ("SchemaA", "SchemaB")
    assert spec.hooks == ("hook_a", "hook_b")
    assert spec.security_deps == ("sec_a", "sec_b")
    assert spec.deps == ("dep_a", "dep_b")
