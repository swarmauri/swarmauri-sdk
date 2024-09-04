import pytest
import numpy as np
from swarmauri.community.tools.concrete.PaCMAPTool import PaCMAPTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'PaCMAPTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.parametrize("X, n_neighbors, n_components, n_iterations, expected_shape, should_raise", [
    (np.random.rand(100, 50), 30, 2, 500, (100, 2), False),  # Valid case: 100 samples, 50 features, reduce to 2D
    (np.random.rand(200, 100), 10, 3, 300, (200, 3), False),  # Valid case: 200 samples, 100 features, reduce to 3D
    (np.random.rand(50, 20), 15, 2, 100, (50, 2), False),  # Valid case: 50 samples, 20 features, reduce to 2D
    (None, 30, 2, 500, None, True),  # Invalid case: X is None, should raise TypeError
    (np.random.rand(100, 50), 30, None, 500, None, True),  # Invalid case: n_components is None, should raise TypeError
])
@pytest.mark.unit
def test_call(X, n_neighbors, n_components, n_iterations, expected_shape, should_raise):
    tool = Tool()
    kwargs = {
        'X': X,
        'n_neighbors': n_neighbors,
        'n_components': n_components,
        'n_iterations': n_iterations,
    }

    if should_raise:
        with pytest.raises(TypeError):
            tool(**kwargs)
    else:
        result = tool(**kwargs)
        assert result.shape == expected_shape
        assert isinstance(result, np.ndarray)

