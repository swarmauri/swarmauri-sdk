import pytest
from cayaml import round_trip_loads


@pytest.mark.xfail(
    reason="YAML directives (%YAML, %TAG, etc.) not yet supported by cayaml."
)
def test_directives():
    """
    Tests handling of YAML directives such as %YAML 1.2, %TAG, etc.
    """
    yaml_str = """
    %YAML 1.2
    %TAG ! tag:example.com,2025:app/
    ---
    !User
    name: "John Doe"
    age: 30
    """
    data = round_trip_loads(yaml_str)
    # The directive might set version or define tags. Minimal parser may ignore them.
    # Just ensure no parse errors and the data is recognized.
    assert data["name"] == "John Doe"
    assert data["age"] == 30
