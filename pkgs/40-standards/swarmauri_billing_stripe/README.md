# swarmauri_billing_stripe

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_stripe</strong></p>
<p align="center">Stripe-backed Swarmauri billing provider for checkout, payments, subscriptions, invoices, refunds, disputes, Connect, and webhooks.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_stripe/"><img alt="pypi: swarmauri_billing_stripe" src="https://img.shields.io/pypi/v/swarmauri_billing_stripe?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_stripe/"><img alt="Monthly PyPI downloads: swarmauri_billing_stripe" src="https://img.shields.io/pypi/dm/swarmauri_billing_stripe?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/README.md"><img alt="README hits: swarmauri_billing_stripe" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_billing_stripe/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_stripe` provides a Stripe-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the official Stripe Python SDK for products, prices, Checkout Sessions, Payment Intents, captures, cancellations, refunds, subscriptions, invoices, Stripe Connect destination charges, disputes, and webhook signature verification.

### Why This Package

Use `swarmauri_billing_stripe` when a Swarmauri application needs production Stripe billing workflows while keeping application code behind provider-neutral billing interfaces. The provider maps Stripe Billing, Checkout, Payment Intents, Refunds, Invoicing, Subscriptions, Connect, and Disputes into Swarmauri refs and specs.

### When to Use

Choose `swarmauri_billing_stripe` when your integration needs stripe-backed Swarmauri billing provider for checkout, payments, subscriptions, invoices, refunds, disputes, Connect, and webhooks. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Stripe-backed provider class registered as `StripeBillingProvider`.
- Product and price creation with metadata support.
- Hosted Checkout Session creation for one-time payments.
- Payment Intent creation with automatic or manual capture.
- Payment capture and cancellation through Stripe Payment Intents.
- Refund creation and lookup through Stripe Refunds.
- Subscription creation and cancellation with Stripe prices.
- Invoice item creation plus invoice lifecycle operations.
- Stripe Connect destination-charge support with application fees.
- Webhook signature verification through `stripe.Webhook.construct_event`.
- Dispute listing for operational review workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_stripe` owns stripe-backed Swarmauri billing provider for checkout, payments, subscriptions, invoices, refunds, disputes, Connect, and webhooks. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `stripe`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_stripe
```

Install with `pip`:

```bash
pip install swarmauri_billing_stripe
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_stripe
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_stripe
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_stripe
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/docs/readme/quick_start.py).

```python
from swarmauri_billing_stripe import StripeBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = StripeBillingProvider(api_key="sk_test_123")

product = provider.create_product(
    ProductSpec(name="Starter", description="Starter subscription"),
    idempotency_key="stripe-prod-001",
)
price = provider.create_price(
    product,
    PriceSpec(
        currency="USD", unit_amount_minor=1000, nickname="Starter monthly"
    ),
    idempotency_key="stripe-price-001",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        customer_email="buyer@example.com",
        idempotency_key="stripe-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_stripe` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/docs/readme/usage.py).

```python
from swarmauri_billing_stripe import StripeBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = StripeBillingProvider(api_key="sk_test_123")

product = provider.create_product(
    ProductSpec(name="Starter", description="Starter subscription"),
    idempotency_key="stripe-prod-001",
)
price = provider.create_price(
    product,
    PriceSpec(
        currency="USD", unit_amount_minor=1000, nickname="Starter monthly"
    ),
    idempotency_key="stripe-price-001",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        customer_email="buyer@example.com",
        idempotency_key="stripe-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.usage -->

Create a product, price, and Stripe Checkout Session:


Create and capture a manual Payment Intent:

```python
from swarmauri_billing_stripe import StripeBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = StripeBillingProvider(api_key="sk_test_123")

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=2500,
        currency="USD",
        payment_method_id="pm_card_visa",
        confirm=True,
        capture=False,
        idempotency_key="stripe-payment-001",
    )
)
captured = provider.capture_payment(payment.id, idempotency_key="stripe-capture-001")

print(payment.status, captured.status)
```

Verify a Stripe webhook signature:

```python
from swarmauri_billing_stripe import StripeBillingProvider

provider = StripeBillingProvider(api_key="sk_test_123")

valid = provider.verify_webhook_signature(
    raw_body=b'{"id":"evt_test","object":"event"}',
    headers={"Stripe-Signature": "t=...,v1=..."},
    secret="whsec_...",
)

print(valid)
```

### Configuration

Configure `swarmauri_billing_stripe` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/swarmauri_billing_stripe/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_stripe` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_stripe` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `StripeBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_stripe` is located in `standards` and owns stripe-backed Swarmauri billing provider for checkout, payments, subscriptions, invoices, refunds, disputes, Connect, and webhooks. Source-declared APIs include `StripeBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_stripe`.

Source-declared exports or types: `StripeBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/swarmauri_billing_stripe/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `StripeBillingProvider` → `swarmauri_billing_stripe.provider:StripeBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
StripeBillingProvider = "swarmauri_billing_stripe.provider:StripeBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_stripe` are `swarmauri-core`, `swarmauri-base`, `stripe`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/swarmauri_billing_stripe/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_stripe` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_stripe`, use the source-declared public interfaces (`StripeBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_stripe` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_stripe`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/swarmauri_billing_stripe/__init__.py). The `swarmauri_billing_stripe` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_stripe` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_stripe` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for stripe-backed Swarmauri billing provider for checkout, payments, subscriptions, invoices, refunds, disputes, Connect, and webhooks.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_stripe` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/swarmauri_billing_stripe/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call live Stripe APIs?**

A: Yes. The provider configures the official `stripe` Python SDK with `api_key` and calls Stripe resources such as `Product`, `Price`, `checkout.Session`, `PaymentIntent`, `Refund`, `Subscription`, `Invoice`, and `Dispute`.

**Q: Which Stripe workflows are supported?**

A: It supports product and price creation, hosted checkout, payment intent creation, manual capture, payment intent cancellation, refund create/retrieve, subscription create/cancel, invoice create/finalize/void/mark-uncollectible, Connect destination charges with application fees, webhook signature validation, and dispute listing.

**Q: What credential is required?**

A: Pass a Stripe secret key as `api_key`, such as a test key beginning with `sk_test_`. Production keys should be provided through secure deployment secrets.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_stripe`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/swarmauri_billing_stripe/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_billing_stripe` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Stripe provider source](swarmauri_billing_stripe/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Stripe API documentation](https://docs.stripe.com/api)

### Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

When expanding Stripe coverage, keep each Swarmauri billing method aligned with the official Stripe Python SDK, document required Stripe account configuration, and add tests for each changed runtime path.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_billing_stripe` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses live Stripe SDK calls. Runtime behavior depends on Stripe account settings, API version, enabled payment methods, test or live mode, Checkout configuration, Connect account setup, and webhook endpoint secrets.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_stripe` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_stripe` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_stripe` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_billing_stripe/NOTICE) for attribution.
<!-- readme-standards:end notices -->
