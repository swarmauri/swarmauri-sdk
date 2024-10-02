from typing import Union, Dict, Any, List, ClassVar, Optional
import numpy as np
from deepface import DeepFace
from pydantic import BaseModel, Field, ValidationError, model_validator
from swarmauri.distances.base.VisionDistanceBase import VisionDistanceBase


class DeepFaceDistance(VisionDistanceBase):
    # Class Variables (Non-Field Attributes)
    allowed_models: ClassVar[List[str]] = [
        "VGG-Face", "Facenet", "Facenet512", "OpenFace", 
        "DeepFace", "DeepID", "Dlib", "ArcFace", 
        "SFace", "GhostFaceNet"
    ]
    VALID_DISTANCE_METRICS: ClassVar[List[str]] = ["cosine", "euclidean", "euclidean_l2"]
    VALID_DETECTOR_BACKENDS: ClassVar[List[str]] = [
        "opencv", "retinaface", "mtcnn", "ssd", 
        "dlib", "mediapipe", "yolov8", "centerface", "skip"
    ]
    VALID_NORMALIZATIONS: ClassVar[List[str]] = [
        "base", "raw", "Facenet", "Facenet2018", 
        "VGGFace", "VGGFace2", "ArcFace"
    ]

    # Default Values
    DEFAULT_DISTANCE_METRIC: ClassVar[str] = "cosine"
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
    distance_metric: str = Field(
        default=DEFAULT_DISTANCE_METRIC,
        description="Distance metric to use for comparison."
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
    def validate_distance_metric(cls, values):
        distance_metric = values.get('distance_metric', cls.DEFAULT_DISTANCE_METRIC)
        if distance_metric not in cls.VALID_DISTANCE_METRICS:
            raise ValueError(
                f"Invalid distance metric '{distance_metric}'. Expected one of {cls.VALID_DISTANCE_METRICS}"
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

    def verify(
        self, 
        img1_path: Union[str, np.ndarray, List[float]], 
        img2_path: Union[str, np.ndarray, List[float]], 
        threshold: Optional[float] = None, 
        silent: bool = False
    ) -> Dict[str, Any]:
        """
        Verifies whether two images represent the same person.

        Args:
            img1_path (Union[str, np.ndarray, List[float]]): Path of the first image or image data.
            img2_path (Union[str, np.ndarray, List[float]]): Path of the second image or image data.
            threshold (float, optional): The similarity threshold.
            silent (bool, optional): If True, suppresses output.

        Returns:
            Dict[str, Any]: A dictionary containing the verification results.
        """
        try:
            result = DeepFace.verify(
                img1_path=img1_path, 
                img2_path=img2_path, 
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                distance_metric=self.distance_metric,
                align=self.align,
                enforce_detection=self.enforce_detection,
                expand_percentage=self.expand_percentage,
                normalization=self.normalization,
                threshold=threshold,
                silent=silent,
                anti_spoofing=self.anti_spoofing
            )
            return result
        except Exception as e:
            # Handle exceptions or log as needed
            raise RuntimeError(f"DeepFace verification failed: {e}") from e
