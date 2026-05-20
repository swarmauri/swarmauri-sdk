![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_tls_unicast/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_tls_unicast/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_tls_unicast/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_tls_unicast.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tls_unicast/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tls_unicast/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_tls_unicast" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tls_unicast/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_tls_unicast?label=swarmauri_transport_tls_unicast&color=green" alt="PyPI - swarmauri_transport_tls_unicast"/></a>
</p>
---

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
