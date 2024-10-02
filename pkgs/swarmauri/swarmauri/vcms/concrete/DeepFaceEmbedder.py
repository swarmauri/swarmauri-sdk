from typing import Union, List, Dict, Any, ClassVar, Optional
import numpy as np
from deepface import DeepFace
from pydantic import BaseModel, Field, ValidationError, model_validator
from swarmauri.embeddings.base.VisionEmbeddingBase import VisionEmbeddingBase


class DeepFaceEmbedder(VisionEmbeddingBase):
    # Class Variables (Non-Field Attributes)
    allowed_models: ClassVar[List[str]] = [
        "VGG-Face", "Facenet", "Facenet512", "OpenFace", 
        "DeepFace", "DeepID", "Dlib", "ArcFace", 
        "SFace", "GhostFaceNet"
    ]
    VALID_DETECTOR_BACKENDS: ClassVar[List[str]] = [
        "opencv", "retinaface", "mtcnn", "ssd", 
        "dlib", "mediapipe", "yolov8", "centerface", "skip"
    ]
    VALID_NORMALIZATIONS: ClassVar[List[str]] = [
        "base", "raw", "Facenet", "Facenet2018", 
        "VGGFace", "VGGFace2", "ArcFace"
    ]

    # Default Values
    DEFAULT_MODEL_NAME: ClassVar[str] = "VGG-Face"
    DEFAULT_DETECTOR_BACKEND: ClassVar[str] = "opencv"
    DEFAULT_ALIGN: ClassVar[bool] = True
    DEFAULT_ENFORCE_DETECTION: ClassVar[bool] = True
    DEFAULT_EXPAND_PERCENTAGE: ClassVar[float] = 0.0
    DEFAULT_NORMALIZATION: ClassVar[str] = "base"
    DEFAULT_ANTI_SPOOFING: ClassVar[bool] = False

    # Pydantic Fields
    model_name: str = Field(
        default=DEFAULT_MODEL_NAME,
        description="Name of the model to use for embedding."
    )
    detector_backend: str = Field(
        default=DEFAULT_DETECTOR_BACKEND,
        description="Backend to use for face detection."
    )
    align: bool = Field(
        default=DEFAULT_ALIGN,
        description="Whether to align the face before processing."
    )
    enforce_detection: bool = Field(
        default=DEFAULT_ENFORCE_DETECTION,
        description="Whether to enforce face detection."
    )
    expand_percentage: float = Field(
        default=DEFAULT_EXPAND_PERCENTAGE,
        description="Percentage to expand the bounding box."
    )
    normalization: str = Field(
        default=DEFAULT_NORMALIZATION,
        description="Normalization method to apply to embeddings."
    )
    anti_spoofing: bool = Field(
        default=DEFAULT_ANTI_SPOOFING,
        description="Enable anti-spoofing measures."
    )

    # Validators
    @model_validator(mode="before")
    @classmethod
    def validate_model_name(cls, values):
        model_name = values.get('model_name', cls.DEFAULT_MODEL_NAME)
        if model_name not in cls.allowed_models:
            raise ValueError(
                f"Invalid model name '{model_name}'. Expected one of {cls.allowed_models}"
            )
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_detector_backend(cls, values):
        detector_backend = values.get('detector_backend', cls.DEFAULT_DETECTOR_BACKEND)
        if detector_backend not in cls.VALID_DETECTOR_BACKENDS:
            raise ValueError(
                f"Invalid detector backend '{detector_backend}'. Expected one of {cls.VALID_DETECTOR_BACKENDS}"
            )
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_normalization(cls, values):
        normalization = values.get('normalization', cls.DEFAULT_NORMALIZATION)
        if normalization not in cls.VALID_NORMALIZATIONS:
            raise ValueError(
                f"Invalid normalization '{normalization}'. Expected one of {cls.VALID_NORMALIZATIONS}"
            )
        return values

    def represent(
        self, 
        img_path: Union[str, np.ndarray], 
        max_faces: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates embeddings for faces in the given image.

        Args:
            img_path (Union[str, np.ndarray]): Path to the image or image data as a NumPy array.
            max_faces (Optional[int]): Maximum number of faces to process. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing face embeddings and related information.
        """
        try:
            result = DeepFace.represent(
                img_path=img_path, 
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
                align=self.align,
                expand_percentage=self.expand_percentage,
                normalization=self.normalization,
                anti_spoofing=self.anti_spoofing,
                max_faces=max_faces
            )
            # Ensure the result is a list of dictionaries
            if isinstance(result, dict):
                return [result]
            return result
        except Exception as e:
            # Handle exceptions or log as needed
            raise RuntimeError(f"DeepFace embedding failed: {e}") from e
