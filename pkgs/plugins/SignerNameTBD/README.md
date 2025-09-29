# SignerNameTBD Plugin

![Swarmauri brand theme](../../../assets/swarmauri.brand.theme.svg)

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](../..)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%E2%80%93%203.12-3776AB.svg)](https://www.python.org/)
[![uv Enabled](https://img.shields.io/badge/uv-ready-8A2BE2.svg)](https://github.com/astral-sh/uv)

## Overview

`SignerNameTBD` packages a composite [`ISigning`](../../base/README.md) implementation that can
route signing and verification requests to one or more concrete Swarmauri signers. It is intended to
act as a lightweight compatibility layer when you need to federate algorithms, or when you want a
single interface that can gracefully fall back to the first available signer in your environment.
The plugin registers a `Signer` component that understands the extended signing surface (bytes,
digests, envelopes, and streams) introduced by the Swarmauri core interfaces.

## Installation

The project ships with extras that pull in common signer implementations for CMS, JWS, OpenPGP, and
PAdES scenarios. Choose the path that matches your tooling preferences:

### Using `uv`

```bash
uv add swm-signernametbd[cms]
```

The example above installs the plugin alongside the CMS-focused signers. Swap `cms` for `jws`,
`openpgp`, or `pades` (or combine them, e.g. `uv add swm-signernametbd[cms,jws]`) to tailor the set
of dependencies. If you only need the aggregator surface, omit the extras entirely: `uv add
swm-signernametbd`.

### Using `pip`

```bash
pip install "swm-signernametbd[openpgp]"
```

`pip` consumers can request the same extras. The quoted form ensures shells do not interpret the
brackets. Installing without extras keeps the footprint minimal while still exposing the aggregated
signing interface.

## Usage

```python
from swarmauri_core.signing import ISigning
from swarmauri_base.signing.SigningBase import SigningBase
from SignerNameTBD.Signer import Signer

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner
from swarmauri_signing_hmac import HmacEnvelopeSigner

# Instantiate the concrete providers you want to delegate to.
ed25519 = Ed25519EnvelopeSigner()
hmac = HmacEnvelopeSigner()

# The aggregator discovers capabilities from ``supports()``.
composite = Signer(providers=[ed25519, hmac], default_alg="Ed25519")

payload = b"example"
keyref = {"kind": "raw_ed25519_sk", "bytes": b"\x00" * 32}

signatures = await composite.sign_bytes(keyref, payload)
assert await composite.verify_bytes(payload, signatures)
```

The `Signer` evaluates every registered provider's `supports()` declaration to decide how to handle
incoming requests. When the caller specifies an `alg` parameter the matching provider is selected;
otherwise, the aggregator falls back to the configured `default_alg` or the sole registered
implementation. Stream inputs are buffered automatically, allowing existing byte-oriented signers to
participate without additional code. Because the composite preserves each provider's feature flags
you can still introspect capabilities (for example, which canonicalization formats are available) by
calling `Signer.supports()`.
