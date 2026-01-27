![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl-billing/">
        <img src="https://img.shields.io/pypi/dm/tigrbl-billing" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_billing/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_billing.svg"/></a>
    <a href="https://pypi.org/project/tigrbl-billing/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl-billing" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl-billing/">
        <img src="https://img.shields.io/pypi/l/tigrbl-billing" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl-billing/">
        <img src="https://img.shields.io/pypi/v/tigrbl-billing?label=tigrbl-billing&color=green" alt="PyPI - tigrbl-billing"/></a>
</p>

---

# Tigrbl Billing 🧾

Full-spectrum billing models, lifecycle operations, and reporting views designed for the Tigrbl platform.

`tigrbl-billing` packages the canonical product catalog, subscription, invoicing, and credit subsystems into a
single distribution so you can drop billing primitives into any Tigrbl deployment.

## Features ✨

- 🗃️ **Unified schema** for products, prices, tiers, usage events, invoices, webhooks, and Stripe entities.
- 🔁 **Lifecycle operations** for subscriptions, invoicing, seat management, grants, and credit charging backed by
  lazily imported ``tigrbl_billing.ops`` helpers.
- 📈 **Analytics-ready views** for ARR, MRR, ARPU, retention cohorts, dunning funnels, revenue attribution, and more.
- 🔌 **Gateway helpers** that assemble multiple metered, tiered, and checkout API apps in a single call.
- ☁️ **Stripe synchronization utilities** to keep local records aligned with upstream events and connected accounts.
- 🧱 **Extensible credit system** covering balance top-offs, usage policies, and ledger management.

## Installation 📦

### Using `uv`

```bash
uv pip install tigrbl-billing
```

### Using `pip`

```bash
pip install tigrbl-billing
```

`tigrbl-billing` supports Python 3.10 through 3.12. Workspace builds can source the sibling `tigrbl` package from this
monorepo using `uv` workspaces.

## Quick Start 🚀

```python
from tigrbl.engine.shortcuts import engine, mem
from tigrbl_billing.api import billing_api

# Build a fully loaded billing app with async support.
app = billing_api.build_billing_app(async_mode=True)

# Or selectively compose feature-specific apps.
from tigrbl_billing import gateway
apps = gateway.build_all_apps(async_mode=True)
product_price_api = apps["product_price"]
```

The exported ASGI apps expose RESTful and JSON-RPC entrypoints backed by the Tigrbl ORM. Models can be imported
individually from `tigrbl_billing.tables` for customization, while operations in `tigrbl_billing.ops` provide
pre-built lifecycle handlers.

## Data Model Highlights 🧱

- **Catalog** – `Product`, `Price`, `PriceTier`, and `Feature` mirror Stripe catalog constructs with local metadata
  extensions.
- **Subscriptions** – `Subscription`, `SubscriptionItem`, and `SeatAllocation` capture plan usage and allocation
  semantics.
- **Usage Tracking** – `UsageEvent` and `UsageRollup` provide granular event ingestion with rollups for metered billing.
- **Invoicing & Payments** – `Invoice`, `InvoiceLineItem`, `PaymentIntent`, and `Refund` manage billing state machines.
- **Stripe Connect** – `ConnectedAccount`, `SplitRule`, `Transfer`, and `ApplicationFee` simplify partner payouts.
- **Credits** – `CustomerBalance`, `BalanceTopOff`, `CreditGrant`, `CreditLedger`, and `CreditUsagePolicy` deliver a
  flexible credit system.

## Operations & Integrations ⚙️

- `tigrbl_billing.ops.subscription_ops` – start, cancel, pause, resume, and trial management.
- `tigrbl_billing.ops.invoice_ops` – finalize, void, and mark invoices uncollectible.
- `tigrbl_billing.ops.usage_ops` – periodic rollups to hydrate ARR/MRR reporting.
- `tigrbl_billing.ops.credit_usage_ops` – charge credits or auto top-off balances.
- `tigrbl_billing.ops.webhook_ops` – ingest Stripe webhook payloads safely.
- `tigrbl_billing.ops.sync_ops` – sync catalog, subscription, and payment data from Stripe.

Pair these operations with the gateway factory to expose separated micro-apps for product pricing, tiered plans, seat
tracking, or checkout experiences.

## API Construction Best Practices 🧩

When composing bespoke billing APIs, import only the operations you need. The
``tigrbl_billing.ops`` package now exposes a lazy loader so operations register
with their bound models only after an API touches them. This keeps global state
clean and avoids double registration.

```python
from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing import ops
from tigrbl_billing.tables.subscription import Subscription

# Touch the exact helpers required by this API.
ops.start_subscription
ops.cancel_subscription


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([Subscription])
    return app
```

Avoid wrapping these helpers with new ``@op_ctx`` decorators—doing so would
rebind the already decorated operations and can lead to duplicate aliases. Load
the helpers, include the relevant models, and the bound operations will be ready
to serve.

## Analytics Views 📊

The `tigrbl_billing.views` package includes ready-to-query SQL views such as:

- `arr_customer` and `arpu_monthly` for revenue optics.
- `cohort_retention` and `dunning_funnel` for lifecycle intelligence.
- `revenue_by_split_rule` and `usage_coverage_ratio` for partner and consumption analytics.

Each view is declared using the Tigrbl ORM spec helpers so they can be materialized or queried directly.

## Development 🛠️

Clone the Swarmauri SDK monorepo and install dependencies with `uv`:

```bash
uv sync
uv run --directory pkgs/standards/tigrbl_billing --package tigrbl-billing ruff format .
uv run --directory pkgs/standards/tigrbl_billing --package tigrbl-billing ruff check .
```

We welcome issues and pull requests that expand the schema, operations, or analytics portfolio.

## License 📜

Apache-2.0. See the [LICENSE](LICENSE) file for details.
