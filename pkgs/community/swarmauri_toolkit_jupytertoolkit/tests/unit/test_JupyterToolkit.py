import pytest
from swarmauri_toolkit_jupytertoolkit.JupyterToolkit import JupyterToolkit


@pytest.mark.unit
def test_class_type():
    """Test the type of JupyterToolkit"""
    assert JupyterToolkit._type == "JupyterToolkit"


@pytest.mark.unit
def test_instance_type():
    """Test the type of JupyterToolkit"""
    assert JupyterToolkit().type == "JupyterToolkit"


@pytest.mark.unit
def test_tools():
    """Test the tools attribute of JupyterToolkit"""
    jupyter_toolkit = JupyterToolkit()
    assert isinstance(jupyter_toolkit.tools, dict)
    assert len(jupyter_toolkit.tools) > 0


@pytest.mark.unit
def test_tool_instantiation():
    """Test the instantiation of tools in JupyterToolkit"""
    jupyter_toolkit = JupyterToolkit()
    for tool in jupyter_toolkit.tools.values():
        assert tool is not None


@pytest.mark.unit
def test_toolkit_registration():
    """Test the registration of JupyterToolkit as a ToolkitBase subclass"""
    assert JupyterToolkit.__bases__[0].__name__ == "ToolkitBase"


@pytest.mark.unit
def test_model_dump_json():
    """Test the model_dump_json method of JupyterToolkit"""
    jupyter_toolkit = JupyterToolkit()
    json_data = jupyter_toolkit.model_dump_json()
    assert isinstance(json_data, str)


@pytest.mark.unit
def test_model_validate_json():
    """Test the model_validate_json method of JupyterToolkit"""
    jupyter_toolkit = JupyterToolkit()
    json_data = jupyter_toolkit.model_dump_json()
    validated_json = JupyterToolkit.model_validate_json(json_data)
    assert validated_json == json_data
