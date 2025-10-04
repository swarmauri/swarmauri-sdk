from tigrbl_spiffe.tables.svid import Svid
from tigrbl_spiffe.tables.registrar import Registrar
from tigrbl_spiffe.tables.bundle import Bundle

def test_tables_exist():
    for cls in (Svid, Registrar, Bundle):
        assert hasattr(cls, "__tablename__")
        assert hasattr(cls, "__resource__")
