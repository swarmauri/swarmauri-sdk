# swarmauri_billing_authorize_net

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_authorize_net</strong></p>
<p align="center">Authorize.Net JSON API backed Swarmauri billing provider for transactions, captures, voids, refunds, customer profiles, and webhook validation.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_authorize_net/"><img alt="pypi: swarmauri_billing_authorize_net" src="https://img.shields.io/pypi/v/swarmauri_billing_authorize_net"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_authorize_net/"><img alt="Monthly PyPI downloads: swarmauri_billing_authorize_net" src="https://img.shields.io/pypi/dm/swarmauri_billing_authorize_net"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/README.md"><img alt="README hits: swarmauri_billing_authorize_net" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_billing_authorize_net/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_authorize_net` provides an Authorize.Net JSON API backed billing provider for Swarmauri payment workflows. It connects Swarmauri billing interfaces to Authorize.Net transaction creation, prior-auth capture, voids, refunds, customer profiles, transaction details, webhook parsing, and HMAC-SHA512 webhook validation.

### Why This Package

`swarmauri_billing_authorize_net` gives billing integrators an Authorize.Net payment provider behind Swarmauri billing interfaces. Applications can authorize, capture, void, refund, create customer profiles, and validate webhook notifications without hard-coding Authorize.Net request payloads throughout the codebase.

### When to Use

Choose `swarmauri_billing_authorize_net` when your integration needs authorize.Net JSON API backed Swarmauri billing provider for transactions, captures, voids, refunds, customer profiles, and webhook validation. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Authorize.Net provider class registered as `AuthorizeNetBillingProvider`.
- JSON API transaction creation for `authCaptureTransaction` and `authOnlyTransaction`.
- Prior authorization capture and void transaction support.
- Refund transaction creation and transaction detail lookup.
- Customer profile creation and retrieval.
- HMAC-SHA512 webhook signature validation using `X-ANET-Signature`.
- Webhook JSON event parsing.
- Uses Swarmauri billing specs and refs from `swarmauri_base.billing`.
- Advertises an explicit subset of `swarmauri_core.billing.Capability`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_authorize_net` owns authorize.Net JSON API backed Swarmauri billing provider for transactions, captures, voids, refunds, customer profiles, and webhook validation. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_authorize_net
```

Install with `pip`:

```bash
pip install swarmauri_billing_authorize_net
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_authorize_net
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_authorize_net
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_authorize_net
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/docs/readme/quick_start.py).

```python
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider
from swarmauri_base.billing import PaymentIntentRequest, RefundRequest

provider = AuthorizeNetBillingProvider(
    api_key="authorize-net-transaction-key",
    login_id="authorize-net-login-id",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=4200,
        currency="USD",
        confirm=True,
        metadata={
            "opaque_data": {
                "dataDescriptor": "COMMON.ACCEPT.INAPP.PAYMENT",
                "dataValue": "opaque-payment-token",
            }
        },
    )
)
refund = provider.create_refund(
    payment,
    RefundRequest(amount_minor=4200),
    idempotency_key="refund-anet-1",
)

print(payment.status, refund["id"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_authorize_net` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/docs/readme/usage.py).

```python
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider
from swarmauri_base.billing import PaymentIntentRequest, RefundRequest

provider = AuthorizeNetBillingProvider(
    api_key="authorize-net-transaction-key",
    login_id="authorize-net-login-id",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=4200,
        currency="USD",
        confirm=True,
        metadata={
            "opaque_data": {
                "dataDescriptor": "COMMON.ACCEPT.INAPP.PAYMENT",
                "dataValue": "opaque-payment-token",
            }
        },
    )
)
refund = provider.create_refund(
    payment,
    RefundRequest(amount_minor=4200),
    idempotency_key="refund-anet-1",
)

print(payment.status, refund["id"])
```
<!-- readme-standards:end example.usage -->

Create and refund an Authorize.Net-style payment:


List payment methods for a customer reference:

```python
from swarmauri_base.billing import CustomerSpec, PaymentMethodSpec
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider

provider = AuthorizeNetBillingProvider(
    api_key="authorize-net-transaction-key",
    login_id="authorize-net-login-id",
)
customer = provider.create_customer(
    CustomerSpec(payload={"email": "buyer@example.com"}),
    idempotency_key="customer-anet-1",
)
payment_method = provider.create_payment_method(
    PaymentMethodSpec(payload={"type": "credit_card"}),
    idempotency_key="pm-anet-1",
)

provider.attach_payment_method_to_customer(customer, payment_method)
methods = provider.list_payment_methods(customer, type="credit_card")

print(customer.id, len(methods))
```

### Configuration

Configure `swarmauri_billing_authorize_net` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/swarmauri_billing_authorize_net/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_authorize_net` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_authorize_net` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AuthorizeNetBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_authorize_net` is located in `community` and owns authorize.Net JSON API backed Swarmauri billing provider for transactions, captures, voids, refunds, customer profiles, and webhook validation. Source-declared APIs include `AuthorizeNetBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_authorize_net`.

Source-declared exports or types: `AuthorizeNetBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/swarmauri_billing_authorize_net/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `AuthorizeNetBillingProvider` → `swarmauri_billing_authorize_net.provider:AuthorizeNetBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
AuthorizeNetBillingProvider = "swarmauri_billing_authorize_net.provider:AuthorizeNetBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_authorize_net` are `swarmauri-core`, `swarmauri-base`, `httpx`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/swarmauri_billing_authorize_net/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_authorize_net` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_authorize_net`, use the source-declared public interfaces (`AuthorizeNetBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_authorize_net` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_authorize_net`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/swarmauri_billing_authorize_net/__init__.py). The `swarmauri_billing_authorize_net` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_authorize_net` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_authorize_net` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for authorize.Net JSON API backed Swarmauri billing provider for transactions, captures, voids, refunds, customer profiles, and webhook validation.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_authorize_net` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/swarmauri_billing_authorize_net/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call Authorize.Net APIs?**

A: Yes for transaction and customer-profile workflows. It posts JSON requests to Authorize.Net sandbox or production endpoints with merchant authentication.

**Q: Which billing areas does it cover?**

A: It covers online payments, prior-auth capture, voids, refunds, customer profile create/get, transaction detail lookup for refunds, webhook parsing, and HMAC-SHA512 signature validation. Some payment-method and reporting helpers remain compatibility placeholders.

**Q: What credentials are required?**

A: Provide `login_id` for the API Login ID and `api_key` for the transaction key. Use `environment="sandbox"` for test accounts and `environment="production"` for live accounts.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_authorize_net`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/swarmauri_billing_authorize_net/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_billing_authorize_net` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/swarmauri_billing_authorize_net/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml) provide the supporting context for `swarmauri_billing_authorize_net`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and provider interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you connect this provider to live Authorize.Net APIs, keep the stub behavior separately testable, document required credentials and webhook behavior, and add tests for every supported billing capability.

### Development Setup

Work from the `pkgs/community/swarmauri_billing_authorize_net` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses live Authorize.Net JSON API calls for transaction and customer-profile workflows. Payment data should be supplied through Accept.js opaque data or other compliant tokenized payloads. Do not place raw card data in application code unless your environment is explicitly PCI scoped.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_authorize_net` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_authorize_net` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_authorize_net` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_authorize_net/NOTICE) for attribution.
<!-- readme-standards:end notices -->
