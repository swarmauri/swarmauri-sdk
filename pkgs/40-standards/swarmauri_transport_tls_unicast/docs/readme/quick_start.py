import ssl
from swarmauri_core.transports import Feature, SecurityMode
from swarmauri_transport_tls_unicast import TlsUnicastTransport

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
transport = TlsUnicastTransport(context)
capabilities = transport.supports()
assert capabilities.security is SecurityMode.TLS
assert Feature.ENCRYPTED in capabilities.features
assert Feature.MUTUAL_AUTH not in capabilities.features
