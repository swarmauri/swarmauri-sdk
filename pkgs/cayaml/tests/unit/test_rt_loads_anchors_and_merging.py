import pytest
from cayaml import round_trip_loads


@pytest.mark.xfail(reason="Anchor &alias and merge not yet supported by cayaml.")
def test_anchors_and_merging():
    """
    Tests YAML anchors (&) and merges (<<).
    Example:

        base: &base
          name: DefaultName
          val: 123

        extended:
          <<: *base
          val: 456
    """
    yaml_str = """
    base: &base
      name: DefaultName
      val: 123

    extended:
      <<: *base
      val: 456
    """
    data = round_trip_loads(yaml_str)
    assert data["extended"]["name"] == "DefaultName"
    assert data["extended"]["val"] == 456
