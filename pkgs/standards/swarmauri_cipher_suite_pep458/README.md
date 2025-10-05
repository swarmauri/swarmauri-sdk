![Swarmauri Brand Theme](https://github.com/swarmauri/swarmauri-sdk/blob/main/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_pep458/">
        <img src="https://img.shields.io/badge/status-planning-blueviolet" alt="Development status" />
    </a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_pep458/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_pep458.svg" alt="Python versions" />
    </a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_pep458/">
        <img src="https://img.shields.io/badge/canonicalization-tuf--json-brightgreen" alt="Canonicalization" />
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_cipher_suite_pep458">
        <img src="https://img.shields.io/badge/pep%20458-policy-blue" alt="PEP 458 policy" />
    </a>
</p>

---

# swarmauri_cipher_suite_pep458

`swarmauri_cipher_suite_pep458` captures the policy surface and algorithm registry
that [PEP 458](https://peps.python.org/pep-0458/) describes for securing Python
package repositories. The suite models canonicalization, allowed algorithms, role
thresholds, and metadata lifetimes so Swarmauri services can negotiate the same
expectations when they sign or verify TUF metadata.

## Highlights

- **Explicit role policies** – Encodes recommended thresholds, expiration windows,
  and algorithm selections for the canonical `root`, `targets`, `snapshot`, and
  `timestamp` metadata roles.
- **Deterministic defaults** – Advertises TUF canonical JSON (`tuf-json`) as the
  canonicalization format and returns Ed25519 as the default online algorithm while
  still supporting RSA-PSS-SHA256 for offline roots.
- **Descriptor normalization** – Produces rich normalized descriptors containing the
  signer implementation hint (`swarmauri_signing_pep458.Pep458Signer`), canonical
  preferences, and caller-specified policy overrides.
- **Compliance metadata** – Surfaces machine readable notes indicating PEP 458 and
  TUF compatibility, enabling automated linting and negotiation between components.

## Installation

### Using `uv`

```bash
uv add swarmauri_cipher_suite_pep458
```

### Using `pip`

```bash
pip install swarmauri_cipher_suite_pep458
```

## Quick Usage

```python
from swarmauri_cipher_suite_pep458 import Pep458CipherSuite

suite = Pep458CipherSuite()

print(suite.features())
# {'suite': 'pep458', 'version': 1, ...}

descriptor = suite.normalize(op="sign", params={"role": "targets", "threshold": 2})
print(descriptor["mapped"]["provider"]["signer"])
# 'swarmauri_signing_pep458.Pep458Signer'
```

Combine the descriptor with instances of `Pep458Signer` to build automated
pipelines that enforce PEP 458's online/offline separation.

## Role Guidance

| Role       | Default Alg        | Threshold | Recommended Expiration |
|------------|--------------------|-----------|------------------------|
| `root`     | `RSA-PSS-SHA256`   | 2         | `P365D`                |
| `targets`  | `Ed25519`          | 1         | `P90D`                 |
| `snapshot` | `Ed25519`          | 1         | `P14D`                 |
| `timestamp`| `Ed25519`          | 1         | `P1D`                  |

These defaults mirror the best practices described in PEP 458, but you can
override them by passing parameters to `normalize` or adjusting the resulting
policy document.

## Relationship to the Signer

This package pairs with `swarmauri_signing_pep458`, which implements the detached
signature algorithm itself. The cipher suite surfaces metadata while the signer
performs the cryptographic operations.

## Development

- Format the code with `ruff format .` and lint with `ruff check . --fix`.
- Add or update unit tests alongside policy changes to validate normalization and
  feature reporting.
- Document any new role guidance in both the README and the `policy()` payload so
  downstream systems stay synchronized.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
