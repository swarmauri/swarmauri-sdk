import pytest
from swarmauri_community.vision_models.concrete.DeepFaceVisionModel import DeepFaceVisionModel 


@pytest.fixture
def deepface_model():
    """Fixture to initialize DeepFaceVisionModel with default settings."""
    return DeepFaceVisionModel()

@pytest.mark.unit
def test_ubc_type(deepface_model):
    assert deepface_model.type == "DeepFaceVisionModel"

@pytest.mark.unit
def test_verify(deepface_model):
    img1_path = 'resources/image1.jpg'  
    img2_path = 'resources/image2.jpg'  
    result = deepface_model.verify(img1_path, img2_path)
    assert 'verified' in result
    assert isinstance(result['verified'], bool)
    assert isinstance(result['distance'], float)

@pytest.mark.unit
def test_find(deepface_model):
    img_path = 'resources/image1.jpg'  
    db_path = 'resources'  
    result = deepface_model.find(img_path, db_path)
    assert isinstance(result, list)
    assert len(result) > 0  

@pytest.mark.unit
def test_represent(deepface_model):
    img_path = 'resources/image1.jpg'  
    result = deepface_model.represent(img_path)
    assert isinstance(result, list)
    assert len(result) > 0  
    assert 'embedding' in result[0]

@pytest.mark.unit
def test_analyze(deepface_model):
    img_path = 'resources/image1.jpg'  
    result = deepface_model.analyze(img_path)
    assert isinstance(result, list)
    assert len(result) > 0  
    assert 'age' in result[0]
    assert 'gender' in result[0]
    assert 'dominant_race' in result[0]
    assert 'emotion' in result[0]


@pytest.mark.unit
def test_extract_faces(deepface_model):
    img_path = 'resources/image1.jpg'  
    result = deepface_model.extract_faces(img_path)
    assert isinstance(result, list)
    assert len(result) > 0  
    assert 'face' in result[0]  


