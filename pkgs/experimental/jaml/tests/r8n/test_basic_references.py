import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(reason="Basic attribute referencing not fully implemented")
def test_basic_self_reference():
    # Test using the self-referencing operator %{ within the same table
    jml = """
[logging]
level = "info"
message = %{level}
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate self-referencing within the same table
    assert data["logging"]["message"] == "info"


@pytest.mark.unit
@pytest.mark.xfail(reason="Global attribute referencing not fully implemented")
def test_basic_global_reference():
    # Test using the global referencing operator ${}
    jml = """
[global]
base_url = "http://example.com"

[api]
endpoint = ${base_url}
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate global reference
    assert data["api"]["endpoint"] == "http://example.com/v1/resource"


@pytest.mark.unit
@pytest.mark.xfail(reason="Same-table attribute referencing not fully implemented")
def test_basic_same_table_reference():
    # Test using the same-table referencing operator @{}
    jml = """
[server]
host = "localhost"
port = 8080
url = @{host}
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate same-table reference
    assert data["server"]["url"] == "localhost"
