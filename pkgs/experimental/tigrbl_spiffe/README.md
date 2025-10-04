# tigrbl-spiffe

SPIFFE/SPIRE plugin for **Tigrbl**. Table/op-centric design:
- Single SVID table with `rotate` op and remote-read delegation
- Registrar and Bundle tables using canonical `read/merge/replace`
- Middleware for identity injection, authn, TLS
- Transport adapter for UDS (agent), HTTP/HTTPS (gateways)

## Install

```bash
uv add tigrbl-spiffe
# or
pip install tigrbl-spiffe
```

## Quickstart

```python
from tigrbl import App
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint

app = App()

plugin = TigrblSpiffePlugin(
    workload_endpoint=Endpoint(scheme="uds", address="unix:///tmp/spire-agent/public/api.sock"),
)
plugin.install(app)
```

See **examples/** for agent fetch, registrar merge, and TLS client usage.
