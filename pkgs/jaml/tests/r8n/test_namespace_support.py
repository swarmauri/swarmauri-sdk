import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(reason="Namespace support not fully implemented")
def test_namespace_basic():
    # Test a basic namespace structure using alternative syntax.
    jml = """
[app]
version = "1.0"
debug = true

[app.db]
host = "localhost"
port = 5432
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["app"]["version"] == "1.0"
    assert data["app"]["debug"] is True
    assert data["app"]["db"]["host"] == "localhost"
    assert data["app"]["db"]["port"] == 5432


@pytest.mark.unit
@pytest.mark.xfail(reason="Dynamic context switching not fully implemented")
def test_namespace_dynamic():
    # Test dynamic context switching using namespace support.
    jml = """
[profile]
active = "production"

[production]
url = "https://prod.example.com"

[development]
url = "http://localhost:8000"
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    active_profile = data["profile"]["active"]
    assert data[active_profile]["url"] == "https://prod.example.com"


@pytest.mark.unit
@pytest.mark.xfail(reason="Namespace aliasing not fully implemented")
def test_namespace_aliasing():
    # Test namespace aliasing for concise access.
    jml = """
[services.api]
endpoint = "/v2/resource"

[api as services.api]
full_url = "{{ api.endpoint }}/full"
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["services"]["api"]["endpoint"] == "/v2/resource"
    assert data["services"]["api"]["full_url"] == "/v2/resource/full"


@pytest.mark.unit
@pytest.mark.xfail(reason="Namespace merging not fully implemented")
def test_namespace_merge():
    # Test namespace merging for dynamic configuration.
    jml = """
[base]
timeout = 30

[production inherits base]
timeout = 60
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["production"]["timeout"] == 60
    assert data["base"]["timeout"] == 30
