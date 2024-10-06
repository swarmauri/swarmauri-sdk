from typing import Union, Dict, Any, List, ClassVar, Literal
import numpy as np
from deepface import DeepFace
from pydantic import BaseModel, Field, ValidationError, model_validator
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

class DeepFaceBase(ComponentBase, BaseModel):

    type: Literal["DeepFaceBase"] = "DeepFaceBase"
    allowed_models: ClassVar[List[str]] = [
        "VGG-Face", "Facenet", "Facenet512", "OpenFace", 
        "DeepFace", "DeepID", "Dlib", "ArcFace", 
        "SFace", "GhostFaceNet"
    ]
    allowed_distance_measurements: ClassVar[List[str]] = ["cosine", "euclidean", "euclidean_l2"]
    allowed_detector_backends: ClassVar[List[str]] = [
        "opencv", "retinaface", "mtcnn", "ssd", 
        "dlib", "mediapipe", "yolov8", "centerface", "skip"
    ]
    allowed_normalizations: ClassVar[List[str]] = [
        "base", "raw", "Facenet", "Facenet2018", 
        "VGGFace", "VGGFace2", "ArcFace"
    ]

    # Default Values
    DEFAULT_MODEL_NAME: ClassVar[str] = "VGG-Face"
    DEFAULT_DISTANCE_METRIC: ClassVar[str] = "cosine"  # Only used in Distance class
    DEFAULT_DETECTOR_BACKEND: ClassVar[str] = "opencv"
    DEFAULT_ALIGN: ClassVar[bool] = True
    DEFAULT_ENFORCE_DETECTION: ClassVar[bool] = True
    DEFAULT_EXPAND_PERCENTAGE: ClassVar[float] = 0.0
    DEFAULT_NORMALIZATION: ClassVar[str] = "base"
    DEFAULT_ANTI_SPOOFING: ClassVar[bool] = False

    # Pydantic Fields
    name: str = Field(
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
        name = values.get('name', cls.DEFAULT_MODEL_NAME)
        if name not in cls.allowed_models:
            raise ValueError(
                f"Invalid model name '{name}'. Expected one of {cls.allowed_models}"
            )
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_detector_backend(cls, values):
        detector_backend = values.get('detector_backend', cls.DEFAULT_DETECTOR_BACKEND)
        if detector_backend not in cls.allowed_detector_backends:
            raise ValueError(
                f"Invalid detector backend '{detector_backend}'. Expected one of {cls.allowed_detector_backends}"
            )
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_normalization(cls, values):
        normalization = values.get('normalization', cls.DEFAULT_NORMALIZATION)
        if normalization not in cls.allowed_normalizations:
            raise ValueError(
                f"Invalid normalization '{normalization}'. Expected one of {cls.allowed_normalizations}"
            )
        return values
