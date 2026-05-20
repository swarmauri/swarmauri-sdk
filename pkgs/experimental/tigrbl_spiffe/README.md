![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_spiffe/">
        <img src="https://static.pepy.tech/badge/tigrbl_spiffe/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_spiffe/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_spiffe.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_spiffe/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_spiffe/">
        <img src="https://img.shields.io/pypi/l/tigrbl_spiffe" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_spiffe/">
        <img src="https://img.shields.io/pypi/v/tigrbl_spiffe?label=tigrbl_spiffe&color=green" alt="PyPI - tigrbl_spiffe"/></a>
</p>
---

# or
pip install tigrbl-spiffe
```

## Quickstart

```python
from tigrbl import TigrblApp
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint

app = TigrblApp()

plugin = TigrblSpiffePlugin(
    workload_endpoint=Endpoint(scheme="uds", address="unix:///tmp/spire-agent/public/api.sock"),
)
plugin.install(app)
```

See **examples/** for agent fetch, registrar merge, and TLS client usage.
