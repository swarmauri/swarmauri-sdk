from typing import Union, List
import pandas as pd
import numpy as np
from deepface import DeepFace

class DeepFaceVectorStore:
    # Class Variables for Defaults and Validations
    VALID_MODELS = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", 
                   "DeepID", "Dlib", "ArcFace", "SFace", "GhostFaceNet"]
    VALID_DISTANCE_METRICS = ["cosine", "euclidean", "euclidean_l2"]
    DEFAULT_MODEL_NAME = "VGG-Face"
    DEFAULT_DETECTOR_BACKEND = "opencv"
    DEFAULT_DISTANCE_METRIC = "cosine"
    DEFAULT_ALIGN = True
    DEFAULT_ENFORCE_DETECTION = True
    DEFAULT_EXPAND_PERCENTAGE = 0
    DEFAULT_NORMALIZATION = "base"
    DEFAULT_ANTI_SPOOFING = False

    def __init__(self, **kwargs):
        model_name = kwargs.get('model_name', self.DEFAULT_MODEL_NAME)
        if model_name not in self.VALID_MODELS:
            raise ValueError(f"Invalid model name. Expected one of {self.VALID_MODELS}")
        self.model_name = model_name

        distance_metric = kwargs.get('distance_metric', self.DEFAULT_DISTANCE_METRIC)
        if distance_metric not in self.VALID_DISTANCE_METRICS:
            raise ValueError(f"Invalid distance metric. Expected one of {self.VALID_DISTANCE_METRICS}")
        self.distance_metric = distance_metric

        self.detector_backend = kwargs.get('detector_backend', self.DEFAULT_DETECTOR_BACKEND)
        self.align = kwargs.get('align', self.DEFAULT_ALIGN)
        self.enforce_detection = kwargs.get('enforce_detection', self.DEFAULT_ENFORCE_DETECTION)
        self.expand_percentage = kwargs.get('expand_percentage', self.DEFAULT_EXPAND_PERCENTAGE)
        self.normalization = kwargs.get('normalization', self.DEFAULT_NORMALIZATION)
        self.anti_spoofing = kwargs.get('anti_spoofing', self.DEFAULT_ANTI_SPOOFING)

    def find(self, img_path: Union[str, np.ndarray], db_path: str,
             threshold: float = None, silent: bool = False,
             refresh_database: bool = True) -> List[pd.DataFrame]:
        result = DeepFace.find(
            img_path=img_path, 
            db_path=db_path, 
            model_name=self.model_name,
            detector_backend=self.detector_backend,
            distance_metric=self.distance_metric,
            align=self.align,
            enforce_detection=self.enforce_detection,
            expand_percentage=self.expand_percentage,
            normalization=self.normalization,
            threshold=threshold,
            silent=silent,
            refresh_database=refresh_database,
            anti_spoofing=self.anti_spoofing
        )
        return result
