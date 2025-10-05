from __future__ import annotations

CAPABILITIES: set[str] = frozenset({
    "x509_svid",
    "jwt_svid",
    "cwt_svid",
    "mtls_client",
    "mtls_server",
    "registration",
    "bundle_sync",
})
