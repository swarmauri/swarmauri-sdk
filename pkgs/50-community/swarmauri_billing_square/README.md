# swarmauri_billing_square

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_square</strong></p>
<p align="center">Square-backed Swarmauri billing provider for catalog items, payment links, payments, refunds, subscriptions, invoices, app fees, and webhooks.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_square/"><img alt="pypi: swarmauri_billing_square" src="https://img.shields.io/pypi/v/swarmauri_billing_square"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_square/"><img alt="Monthly PyPI downloads: swarmauri_billing_square" src="https://img.shields.io/pypi/dm/swarmauri_billing_square"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/README.md"><img alt="README hits: swarmauri_billing_square" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_billing_square/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_square` provides a Square-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the current Square Python SDK for catalog items, item variations, payment links, payments, captures, cancellations, refunds, subscriptions, invoices, application-fee payments, disputes, and webhook signature verification.

### Why This Package

Use `swarmauri_billing_square` when a Swarmauri application needs Square commerce workflows behind provider-neutral billing interfaces. The provider maps Square Catalog, Checkout Payment Links, Payments, Refunds, Subscriptions, Invoices, and Disputes into Swarmauri billing refs so application code can share one billing abstraction across providers.

### When to Use

Choose `swarmauri_billing_square` when your integration needs square-backed Swarmauri billing provider for catalog items, payment links, payments, refunds, subscriptions, invoices, app fees, and webhooks. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Square-backed provider class registered as `SquareBillingProvider`.
- Catalog item and item variation creation for product and price references.
- Payment Link checkout sessions with redirect URL and buyer email support.
- Payment creation, completion, and cancellation through the Payments API.
- Refund creation and lookup through the Refunds API.
- Subscription create/cancel support.
- Invoice create, publish, and cancel support using Square invoice versions.
- Application-fee payment support for marketplace-style platform fees.
- Square webhook verification through `square.utils.webhooks_helper.verify_signature`.
- Dispute listing for operational review workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_square` owns square-backed Swarmauri billing provider for catalog items, payment links, payments, refunds, subscriptions, invoices, app fees, and webhooks. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `squareup`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_square
```

Install with `pip`:

```bash
pip install swarmauri_billing_square
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_square
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_square
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_square
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/docs/readme/quick_start.py).

```python
from swarmauri_billing_square import SquareBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
    environment="sandbox",
)

product = provider.create_product(
    ProductSpec(name="Digital Membership", description="Premium access"),
    idempotency_key="prod-square-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500, nickname="Monthly"),
    idempotency_key="price-square-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/success",
        customer_email="buyer@example.com",
        idempotency_key="checkout-square-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_square` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/docs/readme/usage.py).

```python
from swarmauri_billing_square import SquareBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
    environment="sandbox",
)

product = provider.create_product(
    ProductSpec(name="Digital Membership", description="Premium access"),
    idempotency_key="prod-square-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500, nickname="Monthly"),
    idempotency_key="price-square-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/success",
        customer_email="buyer@example.com",
        idempotency_key="checkout-square-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.usage -->

Create a catalog item, item variation, and Square payment link:


Create and complete a Square payment:

```python
from swarmauri_billing_square import SquareBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=2500,
        currency="USD",
        payment_method_id="cnon:card-nonce-ok",
        capture=False,
        idempotency_key="payment-square-001",
    )
)
captured = provider.capture_payment(payment.id)

print(payment.status, captured.status)
```

Verify a Square webhook signature:

```python
from swarmauri_billing_square import SquareBillingProvider

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
)

valid = provider.verify_webhook_signature(
    raw_body=b'{"merchant_id":"ML123"}',
    headers={
        "X-Square-Hmacsha256-Signature": "signature-from-square",
        "X-Square-Notification-Url": "https://merchant.example/webhooks/square",
    },
    secret="webhook-signature-key",
)

print(valid)
```

### Configuration

Configure `swarmauri_billing_square` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/swarmauri_billing_square/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_square` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_square` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SquareBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_square` is located in `community` and owns square-backed Swarmauri billing provider for catalog items, payment links, payments, refunds, subscriptions, invoices, app fees, and webhooks. Source-declared APIs include `SquareBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_square`.

Source-declared exports or types: `SquareBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/swarmauri_billing_square/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `SquareBillingProvider` → `swarmauri_billing_square.provider:SquareBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
SquareBillingProvider = "swarmauri_billing_square.provider:SquareBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_square` are `swarmauri-core`, `swarmauri-base`, `squareup`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/swarmauri_billing_square/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_square` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_square`, use the source-declared public interfaces (`SquareBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_square` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_square`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/swarmauri_billing_square/__init__.py). The `swarmauri_billing_square` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_square` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_square` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for square-backed Swarmauri billing provider for catalog items, payment links, payments, refunds, subscriptions, invoices, app fees, and webhooks.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_square` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/swarmauri_billing_square/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call live Square APIs?**

A: Yes. It creates a `Square` SDK client with an access token and environment, then calls resources such as `catalog`, `checkout.payment_links`, `payments`, `refunds`, `subscriptions`, `invoices`, and `disputes`.

**Q: Which Square APIs are used?**

A: Products and prices use Catalog objects, hosted checkout uses Payment Links, online payments use Payments, refunds use Refunds, subscription flows use Subscriptions, invoices use Invoices, split-like platform-fee workflows use Payments with `app_fee_money`, and risk checks use webhook signature verification and dispute listing.

**Q: What configuration is required?**

A: Pass `access_token`, `location_id`, and optionally `environment="sandbox"` or `environment="production"`. Use sandbox credentials for development and secure production access tokens through deployment secrets.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_square`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/swarmauri_billing_square/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_billing_square` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Square provider source](swarmauri_billing_square/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Square API documentation](https://developer.squareup.com/reference/square)

### Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

When expanding Square coverage, align each method with the current Square Python SDK, document required permissions and account settings, and add tests for each changed runtime path.

### Development Setup

Work from the `pkgs/50-community/swarmauri_billing_square` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses live Square SDK calls. Runtime behavior depends on Square account configuration, enabled APIs, access-token permissions, valid `location_id` values, catalog object state, invoice versions, and payment status.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_square` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_square` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_square` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_square/NOTICE) for attribution.
<!-- readme-standards:end notices -->
