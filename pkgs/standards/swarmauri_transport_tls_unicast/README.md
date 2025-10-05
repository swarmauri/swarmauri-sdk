# Swarmauri TLS Unicast Transport

![Transport Icon](https://img.shields.io/badge/transport-tls_unicast-4B8BF4.svg)
![Security](https://img.shields.io/badge/security-TLS%2Fmtls-2ECC71.svg)
![Lifecycle](https://img.shields.io/badge/lifecycle-async%20contexts-1E90FF.svg)

The **Swarmauri TLS Unicast Transport** brings encrypted, authenticated
connections to the unified transport lifecycle. It wraps asyncio's TLS streams
with the `.server(...)` / `.client(...)` contexts so you can safely manage
secure sockets directly from the transport.

## Installation

### Using `uv`

```bash
uv add --directory pkgs/standards/swarmauri_transport_tls_unicast swarmauri_transport_tls_unicast
```

### Using `pip`

```bash
pip install swarmauri_transport_tls_unicast
```

## Usage

The snippet below demonstrates creating a mutually-authenticated TLS echo
server and client.

```python
import asyncio
import ssl
from swarmauri_transport_tls_unicast import TlsUnicastTransport

srv_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
srv_ctx.load_cert_chain("srv.pem", "srv.key")
# srv_ctx.verify_mode = ssl.CERT_REQUIRED
# srv_ctx.load_verify_locations("ca.pem")

cli_ctx = ssl.create_default_context()
# cli_ctx.load_cert_chain("cli.pem", "cli.key")

async def main():
    server = TlsUnicastTransport(srv_ctx)

    async def run_server():
        async with server.server(host="0.0.0.0", port=8443):
            data = await server.recv()
            await server.send("peer", b"tls:" + data)

    async def run_client():
        client = TlsUnicastTransport(cli_ctx, sni="localhost")
        async with client.client(host="127.0.0.1", port=8443):
            await client.send("server", b"hello")
            response = await client.recv()
            print(response.decode())

    await asyncio.gather(run_server(), run_client())

asyncio.run(main())
```

Configure the SSL contexts with your own certificates (and CA trust) to enable
TLS or full mTLS verification.
