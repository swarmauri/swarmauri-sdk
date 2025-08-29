![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Remote JWKS Key Provider

Key provider backed by a remote JWKS endpoint with local key management.

## Installation

```bash
pip install swarmauri_keyprovider_remote_jwks
```

## Usage

The provider fetches verification keys from a remote JWKS URL or through an
OpenID Connect (OIDC) issuer.  It also embeds an in-memory key provider to
create and manage local keys.  The example below fetches a JWK from a JWKS
endpoint and prints its public fields:

```python
import asyncio
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider


async def main() -> None:
    provider = RemoteJwksKeyProvider(
        jwks_url="https://example.com/.well-known/jwks.json"
    )

    # Optional: pre-fetch the JWKS; otherwise the first key lookup triggers it
    provider.refresh(force=True)

    jwk = await provider.get_public_jwk("test", version=1)
    print(jwk)


asyncio.run(main())
```

You can also construct the provider from an OIDC issuer.  The provider resolves
the issuer's discovery document to find the JWKS URL:

```python
RemoteJwksKeyProvider(issuer="https://issuer.example.com")

Locally created keys are available via the standard key provider APIs and are
included alongside remote keys when calling `jwks()`.
```
