import warnings
from types import SimpleNamespace
from sqlalchemy import String

from autoapi.v3.engine.shortcuts import engine as engine_factory, mem
from autoapi.v3.bindings.api.include import include_model
from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.specs import IO, S, acol


class _Tenant(Base, GUIDPk):
    __tablename__ = "tenant_dup"
    __allow_unmapped__ = True
    name = acol(
        storage=S(type_=String, nullable=False),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )


def _make_api():
    engine = engine_factory(mem(async_=False))
    raw_engine, _ = engine.raw()
    _Tenant.__table__.create(bind=raw_engine)
    return SimpleNamespace(app=None)


def test_include_model_twice_has_unique_operation_ids():
    api = _make_api()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        include_model(api, _Tenant, mount_router=False)
        include_model(api, _Tenant, mount_router=False)
    assert not any("Duplicate Operation ID" in str(warn.message) for warn in w)
