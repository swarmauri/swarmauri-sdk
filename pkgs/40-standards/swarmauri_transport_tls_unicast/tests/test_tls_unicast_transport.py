import ssl

from swarmauri_core.transports import Feature, SecurityMode
from swarmauri_transport_tls_unicast import TlsUnicastTransport


def test_tls_supports_tls_features() -> None:
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    transport = TlsUnicastTransport(ctx)

    capabilities = transport.supports()

    assert capabilities.security is SecurityMode.TLS
    assert Feature.ENCRYPTED in capabilities.features
    assert Feature.MUTUAL_AUTH not in capabilities.features


def test_tls_supports_mutual_tls_features() -> None:
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.verify_mode = ssl.CERT_REQUIRED

    transport = TlsUnicastTransport(ctx)
    capabilities = transport.supports()

    assert capabilities.security is SecurityMode.MTLS
    assert Feature.MUTUAL_AUTH in capabilities.features
