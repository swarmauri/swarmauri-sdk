import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(
    reason="Conditional table blocks with context attributes not fully implemented"
)
def test_conditional_block_with_external_context():
    # Test conditional block using external context variable ${}
    jml = """
[~(${env} == "production")]
host = "prod-db.example.com"
port = 5432

[~(${env} == "development")]
host = "localhost"
port = 5432
    """.strip()

    context = {"env": "production"}
    ast = round_trip_loads(jml, context=context)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate production environment configuration
    assert data["prod-db.example.com"]["port"] == 5432


@pytest.mark.unit
@pytest.mark.xfail(
    reason="Conditional feature toggle using context not fully implemented"
)
def test_conditional_feature_toggle_with_context():
    # Test feature toggle using context variable ${}
    jml = """
[~(${enable_logging})]
level = "debug"
output = "console"

[~(not ${enable_logging})]
level = "none"
output = "null"
    """.strip()

    context = {"enable_logging": True}
    ast = round_trip_loads(jml, context=context)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate logging configuration when enabled
    assert data["debug"]["output"] == "console"


@pytest.mark.unit
@pytest.mark.xfail(
    reason="Conditional blocks using same-table context not fully implemented"
)
def test_conditional_block_with_same_table_context():
    # Test conditional block using same-table context attribute @{base}
    jml = """
[config]
base = "/usr/local"

[~(@{base} == "/usr/local")]
path = "@{base}/app"
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate same-table context condition
    assert data["/usr/local/app"]["path"] == "/usr/local/app"
