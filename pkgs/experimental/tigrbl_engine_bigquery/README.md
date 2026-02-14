# tigrbl_engine_bigquery

A BigQuery engine plugin for **tigrbl**. This package registers a new engine kind
`"bigquery"` that tigrbl auto-discovers via the `tigrbl.engine` entry-point group.

## Installation

```bash
pip install tigrbl_engine_bigquery
```

## Usage

Once installed, just refer to `kind="bigquery"` in your engine spec:

```python
from tigrbl.engine.engine_spec import EngineSpec

spec = EngineSpec(kind="bigquery", mapping={"project": "my-gcp-project", "default_dataset": "analytics"})
provider = spec.to_provider()
engine, make_session = provider.ensure()   # triggers external plugin registration
session = make_session()                   # returns a BigQuerySession

# Optionally run SQL via the session (see session.query method stub)
```

This package exposes:
- `BigQueryEngine` (engine handle/config)
- `BigQuerySession` (simple session wrapper)
- `bigquery_engine` (builder used by tigrbl)
- `register()` (called by tigrbl’s plugin loader)
