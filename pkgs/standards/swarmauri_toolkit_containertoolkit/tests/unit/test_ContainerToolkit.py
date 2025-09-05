import pytest
from swarmauri_toolkit_containertoolkit import ContainerToolkit


@pytest.mark.unit
def test_class_type():
    assert ContainerToolkit._type == "ContainerToolkit"


@pytest.mark.unit
def test_instance_type():
    assert ContainerToolkit().type == "ContainerToolkit"


@pytest.mark.unit
def test_tools():
    toolkit = ContainerToolkit()
    assert set(toolkit.tools.keys()) == {
        "ContainerNewSessionTool",
        "ContainerFeedCharsTool",
        "ContainerMakePrTool",
    }


@pytest.mark.unit
def test_toolkit_registration():
    assert ContainerToolkit.__bases__[0].__name__ == "ToolkitBase"


@pytest.mark.unit
def test_serialization():
    toolkit = ContainerToolkit()
    data = toolkit.model_dump_json()
    assert toolkit.id == ContainerToolkit.model_validate_json(data).id
