# swarmauri_billing_razorpay

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_razorpay</strong></p>
<p align="center">Razorpay-backed Swarmauri billing provider for payment links, orders, capture, refunds, subscriptions, invoices, transfers, and webhooks.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_razorpay/"><img alt="pypi: swarmauri_billing_razorpay" src="https://img.shields.io/pypi/v/swarmauri_billing_razorpay"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_razorpay/"><img alt="Monthly PyPI downloads: swarmauri_billing_razorpay" src="https://img.shields.io/pypi/dm/swarmauri_billing_razorpay"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/README.md"><img alt="README hits: swarmauri_billing_razorpay" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_billing_razorpay/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_razorpay` provides a Razorpay-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the Razorpay Python SDK for items, payment links, orders, payment capture, refunds, subscriptions, invoices, Route transfers, disputes, and webhook signature verification.

### Why This Package

Use `swarmauri_billing_razorpay` when a Swarmauri application needs Razorpay payment flows while keeping application code behind provider-neutral Swarmauri billing interfaces. The provider lets payment links, orders, subscriptions, invoices, refunds, Route transfers, and dispute checks share the same calling style as other Swarmauri billing providers.

### When to Use

Choose `swarmauri_billing_razorpay` when your integration needs razorpay-backed Swarmauri billing provider for payment links, orders, capture, refunds, subscriptions, invoices, transfers, and webhooks. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Razorpay-backed provider class registered as `RazorpayBillingProvider`.
- Item-based product and price creation.
- Payment Link checkout sessions with customer email support.
- Order creation for online payment initialization.
- Payment capture that fetches the authorized payment amount before calling Razorpay capture.
- Refund creation and refund lookup through Razorpay refund APIs.
- Subscription create/cancel support.
- Invoice create, issue, and cancel operations.
- Route transfer support for split-payment workflows.
- Webhook signature verification with `X-Razorpay-Signature` and HMAC-SHA256.
- Dispute listing through Razorpay disputes.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_razorpay` owns razorpay-backed Swarmauri billing provider for payment links, orders, capture, refunds, subscriptions, invoices, transfers, and webhooks. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `razorpay`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_razorpay
```

Install with `pip`:

```bash
pip install swarmauri_billing_razorpay
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_razorpay
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_razorpay
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_razorpay
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/docs/readme/quick_start.py).

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = RazorpayBillingProvider(
    api_key="razorpay",
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

product = provider.create_product(
    ProductSpec(name="Analytics Plan", description="Advanced dashboards"),
    idempotency_key="razorpay-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="INR", unit_amount_minor=49900, nickname="Quarterly"),
    idempotency_key="razorpay-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/razorpay/callback",
        customer_email="buyer@example.com",
        idempotency_key="razorpay-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_razorpay` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/docs/readme/usage.py).

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = RazorpayBillingProvider(
    api_key="razorpay",
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

product = provider.create_product(
    ProductSpec(name="Analytics Plan", description="Advanced dashboards"),
    idempotency_key="razorpay-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="INR", unit_amount_minor=49900, nickname="Quarterly"),
    idempotency_key="razorpay-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/razorpay/callback",
        customer_email="buyer@example.com",
        idempotency_key="razorpay-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.usage -->

Create a product, price, and Razorpay payment link:


Create an order-backed payment intent:

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = RazorpayBillingProvider(
    api_key="razorpay",
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=49900,
        currency="INR",
        idempotency_key="receipt-1001",
    )
)

print(payment.id, payment.status)
```

Create a partial refund:

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import PaymentRef, RefundRequest

provider = RazorpayBillingProvider(
    api_key="razorpay",
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

refund = provider.create_refund(
    PaymentRef(id="pay_123", provider="razorpay"),
    RefundRequest(amount_minor=1000, reason="Customer request"),
    idempotency_key="refund-1001",
)

print(refund["id"], refund["status"])
```

### Configuration

Configure `swarmauri_billing_razorpay` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/swarmauri_billing_razorpay/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_razorpay` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_razorpay` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `RazorpayBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_razorpay` is located in `community` and owns razorpay-backed Swarmauri billing provider for payment links, orders, capture, refunds, subscriptions, invoices, transfers, and webhooks. Source-declared APIs include `RazorpayBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_razorpay`.

Source-declared exports or types: `RazorpayBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/swarmauri_billing_razorpay/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `RazorpayBillingProvider` → `swarmauri_billing_razorpay.provider:RazorpayBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
RazorpayBillingProvider = "swarmauri_billing_razorpay.provider:RazorpayBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_razorpay` are `swarmauri-core`, `swarmauri-base`, `razorpay`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/swarmauri_billing_razorpay/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_razorpay` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_razorpay`, use the source-declared public interfaces (`RazorpayBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_razorpay` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_razorpay`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/swarmauri_billing_razorpay/__init__.py). The `swarmauri_billing_razorpay` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_razorpay` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_razorpay` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for razorpay-backed Swarmauri billing provider for payment links, orders, capture, refunds, subscriptions, invoices, transfers, and webhooks.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_razorpay` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/swarmauri_billing_razorpay/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call live Razorpay APIs?**

A: Yes. The provider creates a `razorpay.Client` with `key_id` and `key_secret`, then calls SDK resources such as `item`, `payment_link`, `order`, `payment`, `subscription`, `invoice`, `refund`, and `dispute`.

**Q: Which Razorpay products map to Swarmauri billing flows?**

A: Products and prices use Razorpay Items, hosted checkout uses Payment Links, payment intents use Orders, capture/refund use Payments and Refunds APIs, subscription flows use Subscriptions, invoicing uses Invoices, marketplace transfer flows use Route payment transfers, and risk checks use webhook signatures and disputes.

**Q: What credentials are required?**

A: Pass Razorpay API credentials as `key_id` and `key_secret`. Use test mode keys for development and load production keys from secure deployment secrets.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_razorpay`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/swarmauri_billing_razorpay/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_billing_razorpay` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Razorpay provider source](swarmauri_billing_razorpay/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Razorpay API documentation](https://razorpay.com/docs/api/)

### Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

When expanding Razorpay coverage, keep each Swarmauri billing method aligned with the corresponding Razorpay SDK resource, document required credentials and account configuration, and add tests for each changed runtime path.

### Development Setup

Work from the `pkgs/50-community/swarmauri_billing_razorpay` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses live Razorpay SDK calls. Runtime behavior depends on Razorpay account settings, enabled products, API credentials, dashboard capture settings, and the status of each payment, order, invoice, subscription, or Route transfer.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_razorpay` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_razorpay` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_razorpay` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_razorpay/NOTICE) for attribution.
<!-- readme-standards:end notices -->
