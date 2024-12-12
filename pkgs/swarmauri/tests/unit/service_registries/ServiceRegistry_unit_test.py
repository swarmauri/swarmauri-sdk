import pytest
from swarmauri.service_registries.concrete.ServiceRegistry import ServiceRegistry


@pytest.fixture
def service_registry():
    return ServiceRegistry()

@pytest.mark.unit
def test_ubc_resource(service_registry):
    assert service_registry.resource == "ServiceRegistry"


@pytest.mark.unit
def test_ubc_type(service_registry):
    assert service_registry.type == "ServiceRegistry"


@pytest.mark.unit
def test_serialization(service_registry):
    assert service_registry.id == service_registry.model_validate_json(service_registry.model_dump_json()).id


def test_register_service(service_registry):
    service_registry.register_service("auth", {"role": "authentication"})
    assert service_registry.services["auth"] == {"role": "authentication"}


def test_get_service(service_registry):
    service_registry.register_service("auth", {"role": "authentication"})
    service = service_registry.get_service("auth")
    assert service == {"role": "authentication"}
    assert service_registry.get_service("nonexistent") is None


def test_get_services_by_roles(service_registry):
    service_registry.register_service("auth", {"role": "authentication"})
    service_registry.register_service("db", {"role": "database"})
    recipients = service_registry.get_services_by_roles(["authentication"])
    assert recipients == ["auth"]
    recipients = service_registry.get_services_by_roles(["database"])
    assert recipients == ["db"]
    recipients = service_registry.get_services_by_roles(
        ["authentication", "database"]
    )
    assert set(recipients) == {"auth", "db"}
