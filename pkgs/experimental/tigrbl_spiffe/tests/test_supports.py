from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint

def test_supports_has_core_caps():
    p = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="http", address="http://example"))
    caps = p.supports()
    assert "x509_svid" in caps
    assert "jwt_svid" in caps
    assert "bundle_sync" in caps
