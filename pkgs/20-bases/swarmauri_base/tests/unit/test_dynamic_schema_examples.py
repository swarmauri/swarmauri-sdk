"""Executable examples for dynamic schema and serialization support."""

import json
import sqlite3
from typing import Literal

import pytest

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import DynamicBase, SubclassUnion


@ComponentBase.register_model()
class DynamicSchemaExampleBase(ComponentBase):
    """Base family used by docs examples."""

    type: Literal["DynamicSchemaExampleBase"] = "DynamicSchemaExampleBase"
    label: str


@ComponentBase.register_type(
    DynamicSchemaExampleBase, "DynamicSchemaExampleApiSource"
)
class DynamicSchemaExampleApiSource(DynamicSchemaExampleBase):
    """Example component configured from an API payload."""

    type: Literal["DynamicSchemaExampleApiSource"] = (
        "DynamicSchemaExampleApiSource"
    )
    endpoint: str
    auth_required: bool = True


@ComponentBase.register_type(
    DynamicSchemaExampleBase, "DynamicSchemaExampleDatabaseSource"
)
class DynamicSchemaExampleDatabaseSource(DynamicSchemaExampleBase):
    """Example component persisted in a database."""

    type: Literal["DynamicSchemaExampleDatabaseSource"] = (
        "DynamicSchemaExampleDatabaseSource"
    )
    table: str
    primary_key: str


@ComponentBase.register_model()
class DynamicSchemaExampleEnvelope(ComponentBase):
    """Envelope that can hold any registered example component kin."""

    type: Literal["DynamicSchemaExampleEnvelope"] = (
        "DynamicSchemaExampleEnvelope"
    )
    component: SubclassUnion[DynamicSchemaExampleBase]


class ConfigHydratingFactory:
    """Small test-local factory that hydrates specs through the dynamic
    envelope."""

    def create_from_spec(self, spec: dict) -> DynamicSchemaExampleBase:
        envelope = DynamicSchemaExampleEnvelope.model_validate(
            {"component": spec, "type": "DynamicSchemaExampleEnvelope"}
        )
        return envelope.component


@pytest.mark.unit
def test_registered_subclasses_appear_in_dynamic_json_schema():
    """Registering component kin expands the JSON Schema union."""

    @ComponentBase.register_type(
        DynamicSchemaExampleBase, "DynamicSchemaExampleQueueSource"
    )
    class DynamicSchemaExampleQueueSource(DynamicSchemaExampleBase):
        type: Literal["DynamicSchemaExampleQueueSource"] = (
            "DynamicSchemaExampleQueueSource"
        )
        queue_name: str

    schema = DynamicSchemaExampleEnvelope.model_json_schema()
    schema_text = json.dumps(schema)

    assert issubclass(DynamicSchemaExampleBase, DynamicBase)
    assert "DynamicSchemaExampleApiSource" in schema_text
    assert "DynamicSchemaExampleDatabaseSource" in schema_text
    assert "DynamicSchemaExampleQueueSource" in schema_text
    assert "discriminator" in schema_text


@pytest.mark.unit
def test_factory_hydrates_concrete_component_from_serialized_spec():
    """Factories can hydrate concrete kin without handwritten type switches."""

    factory = ConfigHydratingFactory()
    component = factory.create_from_spec(
        {
            "type": "DynamicSchemaExampleApiSource",
            "label": "primary api",
            "endpoint": "https://api.example.test",
            "auth_required": False,
        }
    )

    assert isinstance(component, DynamicSchemaExampleApiSource)
    assert component.endpoint == "https://api.example.test"
    assert component.auth_required is False


@pytest.mark.unit
def test_api_payload_validation_preserves_concrete_component_type():
    """
    API envelopes keep the concrete component instead of returning a dict.
    """

    payload = {
        "type": "DynamicSchemaExampleEnvelope",
        "component": {
            "type": "DynamicSchemaExampleDatabaseSource",
            "label": "analytics table",
            "table": "events",
            "primary_key": "event_id",
        },
    }

    envelope = DynamicSchemaExampleEnvelope.model_validate(payload)

    assert isinstance(envelope.component, DynamicSchemaExampleDatabaseSource)
    assert envelope.component.table == "events"
    assert envelope.component.primary_key == "event_id"


@pytest.mark.unit
def test_database_persistence_round_trips_concrete_component_json():
    """Persisted JSON can restore the same concrete kin later."""

    original = DynamicSchemaExampleEnvelope(
        component=DynamicSchemaExampleApiSource(
            label="remote api", endpoint="https://api.example.test"
        )
    )
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE component_specs (payload TEXT NOT NULL)")
    db.execute(
        "INSERT INTO component_specs (payload) VALUES (?)",
        (original.model_dump_json(),),
    )

    stored_json = db.execute("SELECT payload FROM component_specs").fetchone()[
        0
    ]
    restored = DynamicSchemaExampleEnvelope.model_validate_json(stored_json)

    assert isinstance(restored.component, DynamicSchemaExampleApiSource)
    assert restored.component.endpoint == original.component.endpoint
    assert restored.component.type == original.component.type


@pytest.mark.unit
def test_yaml_and_toml_configs_hydrate_same_concrete_component():
    """YAML and TOML configs use the same discriminator path as JSON."""

    yaml_envelope = DynamicSchemaExampleEnvelope.model_validate_yaml(
        """
        type: DynamicSchemaExampleEnvelope
        component:
          type: DynamicSchemaExampleApiSource
          label: yaml api
          endpoint: https://yaml.example.test
          auth_required: false
        """
    )
    toml_envelope = DynamicSchemaExampleEnvelope.model_validate_toml(
        """
        type = "DynamicSchemaExampleEnvelope"

        [component]
        type = "DynamicSchemaExampleApiSource"
        label = "toml api"
        endpoint = "https://toml.example.test"
        auth_required = false
        """
    )

    assert isinstance(yaml_envelope.component, DynamicSchemaExampleApiSource)
    assert isinstance(toml_envelope.component, DynamicSchemaExampleApiSource)
    assert yaml_envelope.component.endpoint == "https://yaml.example.test"
    assert toml_envelope.component.endpoint == "https://toml.example.test"
    assert "DynamicSchemaExampleApiSource" in yaml_envelope.model_dump_yaml()
    assert "DynamicSchemaExampleApiSource" in toml_envelope.model_dump_toml()
