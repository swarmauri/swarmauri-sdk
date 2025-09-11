import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(reason="F-string reference syntax not fully implemented")
def test_fstring_static_reference():
    # Test the f-string syntax with static reference
    jml = """
[paths]
base = "/home/user"
config = f"${base}/config.toml"
log = f"${base}/logs/app.log"
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate f-string reference resolution
    assert data["paths"]["config"] == "/home/user/config.toml"
    assert data["paths"]["log"] == "/home/user/logs/app.log"


@pytest.mark.unit
@pytest.mark.xfail(reason="Concatenated reference syntax not fully implemented")
def test_concatenated_static_reference():
    # Test the concatenated syntax with static reference
    jml = """
[paths]
base = "/home/user"
config = ${base} + '/config.toml'
log = ${base} + '/logs/app.log'
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate concatenated reference resolution
    assert data["paths"]["config"] == "/home/user/config.toml"
    assert data["paths"]["log"] == "/home/user/logs/app.log"


@pytest.mark.unit
@pytest.mark.xfail(reason="Mixed reference syntax not fully implemented")
def test_mixed_static_reference():
    # Test both f-string and concatenated syntax together
    jml = """
[paths]
base = "/home/user"
config_fstring = f"${base}/config.toml"
config_concat = ${base} + '/config.toml'
log_fstring = f"${base}/logs/app.log"
log_concat = ${base} + '/logs/app.log'
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate both f-string and concatenated references
    assert data["paths"]["config_fstring"] == "/home/user/config.toml"
    assert data["paths"]["config_concat"] == "/home/user/config.toml"
    assert data["paths"]["log_fstring"] == "/home/user/logs/app.log"
    assert data["paths"]["log_concat"] == "/home/user/logs/app.log"
