# Dynamic Schemas and Typed Serialization

Swarmauri components are designed to cross process boundaries without losing
their concrete kin. A component can be initialized from JSON, YAML, or TOML,
dumped back to those formats, and restored with its `type` discriminator intact.

That is a core platform strength for extensible systems. Factories, HTTP APIs,
queues, and databases often only see serialized payloads. Without a dynamic
schema layer, each boundary has to choose between untyped dictionaries or a
manual switch such as `if type == "ApiConnector"`. Both approaches drift as new
component classes become available.

Swarmauri solves this with `DynamicBase`, `ComponentBase.register_model(...)`,
`ComponentBase.register_type(...)`, and `SubclassUnion[...]`. Registered kin are
available to discriminated unions, and Pydantic can emit JSON Schema for the
current runtime surface.

## Define a Typed Component Family

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_model()
class DataSource(ComponentBase):
    type: Literal["DataSource"] = "DataSource"
    label: str


@ComponentBase.register_type(DataSource, "ApiDataSource")
class ApiDataSource(DataSource):
    type: Literal["ApiDataSource"] = "ApiDataSource"
    endpoint: str
    auth_required: bool = True


@ComponentBase.register_type(DataSource, "TableDataSource")
class TableDataSource(DataSource):
    type: Literal["TableDataSource"] = "TableDataSource"
    table: str
    primary_key: str
```

## Carry Concrete Kin Through an Envelope

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion


@ComponentBase.register_model()
class DataSourceEnvelope(ComponentBase):
    type: Literal["DataSourceEnvelope"] = "DataSourceEnvelope"
    component: SubclassUnion[DataSource]


envelope = DataSourceEnvelope.model_validate(
    {
        "type": "DataSourceEnvelope",
        "component": {
            "type": "ApiDataSource",
            "label": "orders api",
            "endpoint": "https://api.example.test/orders",
            "auth_required": False,
        },
    }
)

assert isinstance(envelope.component, ApiDataSource)
assert "ApiDataSource" in str(DataSourceEnvelope.model_json_schema())
```

The envelope field is typed as the base family, but the runtime value is the
registered concrete subclass. The JSON Schema includes the available `type`
choices instead of a stale hand-written schema.

## Factory Hydration

Factories can hydrate serialized component specs through the typed envelope
instead of owning a switch for every possible kin class.

```python
class ConfigHydratingFactory:
    def create_from_spec(self, spec: dict) -> DataSource:
        envelope = DataSourceEnvelope.model_validate(
            {"type": "DataSourceEnvelope", "component": spec}
        )
        return envelope.component


factory = ConfigHydratingFactory()
component = factory.create_from_spec(
    {
        "type": "ApiDataSource",
        "label": "orders api",
        "endpoint": "https://api.example.test/orders",
    }
)

assert isinstance(component, ApiDataSource)
```

The factory does not need to know every subclass. New registered kin can become
available to the schema and hydration path without rewriting factory control
flow.

## API Payloads

The same model shape works for HTTP request or response bodies. An API handler
can validate a base-family payload and still receive the concrete subclass.

```python
payload = {
    "type": "DataSourceEnvelope",
    "component": {
        "type": "TableDataSource",
        "label": "warehouse events",
        "table": "events",
        "primary_key": "event_id",
    },
}

validated = DataSourceEnvelope.model_validate(payload)

assert isinstance(validated.component, TableDataSource)
assert validated.component.table == "events"
```

Without this pattern, the handler usually receives `dict[str, Any]` and must
reconstruct typed objects manually.

## Database Persistence

Persist component specs as JSON and restore them later through the same typed
path.

```python
import sqlite3

original = DataSourceEnvelope(
    component=ApiDataSource(
        label="orders api",
        endpoint="https://api.example.test/orders",
    )
)

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE component_specs (payload TEXT NOT NULL)")
db.execute(
    "INSERT INTO component_specs (payload) VALUES (?)",
    (original.model_dump_json(),),
)

stored_json = db.execute("SELECT payload FROM component_specs").fetchone()[0]
restored = DataSourceEnvelope.model_validate_json(stored_json)

assert isinstance(restored.component, ApiDataSource)
assert restored.component.endpoint == original.component.endpoint
```

The database stores portable JSON, while Swarmauri restores the concrete Python
component when the payload is loaded.

## JSON, YAML, and TOML Configs

`ComponentBase` includes YAML and TOML helpers alongside Pydantic's JSON
support. The same discriminator shape can be used in operator-friendly config
files.

```python
yaml_config = """
type: DataSourceEnvelope
component:
  type: ApiDataSource
  label: yaml api
  endpoint: https://yaml.example.test
  auth_required: false
"""

toml_config = """
type = "DataSourceEnvelope"

[component]
type = "ApiDataSource"
label = "toml api"
endpoint = "https://toml.example.test"
auth_required = false
"""

from_yaml = DataSourceEnvelope.model_validate_yaml(yaml_config)
from_toml = DataSourceEnvelope.model_validate_toml(toml_config)

assert isinstance(from_yaml.component, ApiDataSource)
assert isinstance(from_toml.component, ApiDataSource)
```

This keeps one component contract across JSON APIs, YAML deployment files, TOML
project config, and JSON database storage.
