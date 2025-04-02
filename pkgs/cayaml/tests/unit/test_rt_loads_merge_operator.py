import pytest
from cayaml import round_trip_loads


@pytest.mark.xfail(reason="Merge operator '<<:' not yet supported by cayaml.")
def test_merge_operator():
    """
    Tests the merge operator explicitly in a scenario with multiple merges.
    Example:

        default: &default
          key1: val1
          key2: val2

        override: &override
          key2: overridden

        combined:
          <<: [*default, *override]
          key3: newval
    """
    yaml_str = """
    default: &default
      key1: val1
      key2: val2

    override: &override
      key2: overridden

    combined:
      <<: [*default, *override]
      key3: newval
    """
    data = round_trip_loads(yaml_str)
    assert data["combined"]["key1"] == "val1"
    assert data["combined"]["key2"] == "overridden"
    assert data["combined"]["key3"] == "newval"
