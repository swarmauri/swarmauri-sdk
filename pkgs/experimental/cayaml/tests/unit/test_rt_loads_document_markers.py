import pytest
from cayaml import round_trip_loads, round_trip_loads_all


@pytest.mark.unit
def test_rt_single_document_selection():
    """
    Tests parsing multiple documents from a single YAML string.
    Example:

        ---
        doc1:
          key: value1
        ---
        doc2:
          key: value2
    """
    yaml_str = """
    ---
    doc1:
      key: value1
    ---
    doc2:
      key: value2
    """
    data = round_trip_loads(yaml_str)
    assert not isinstance(data, list), "Expecting a single document"


@pytest.mark.unit
def test_rt_loads_document_markers():
    """
    Tests parsing multiple documents from a single YAML string.
    Example:

        ---
        doc1:
          key: value1
        ---
        doc2:
          key: value2
    """
    yaml_str = """
    ---
    doc1:
      key: value1
    ---
    doc2:
      key: value2
    """
    data = round_trip_loads_all(yaml_str)
    assert isinstance(data, list), "Expecting a list of separate documents"
    assert len(data) == 2
    assert data[0]["doc1"]["key"] == "value1"
    assert data[1]["doc2"]["key"] == "value2"
