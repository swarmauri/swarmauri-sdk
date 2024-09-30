from typing import List, Dict, Any, Union, Literal
import numpy as np
import pandas as pd
from deepface import DeepFace

class DeepFaceVisionModel:
    
    """
    A vision model based on DeepFace for face-related tasks such as verification, recognition,
    embedding extraction, and face analysis. Supports a range of backends, models, and distance metrics.
    """
    
    type: Literal["DeepFaceVisionModel"] = "DeepFaceVisionModel"
    
    VALID_MODELS = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "Dlib", "ArcFace", "SFace", "GhostFaceNet"]
    VALID_DISTANCE_METRICS = ["cosine", "euclidean", "euclidean_l2"]
    VALID_DETECTOR_BACKENDS = ["opencv", "retinaface", "mtcnn", "ssd", "dlib", "mediapipe", "yolov8", "centerface", "skip"]
    VALID_NORMALIZATIONS = ["base", "raw", "Facenet", "Facenet2018", "VGGFace", "VGGFace2", "ArcFace"]
    
    def __init__(self, model_name: str = "VGG-Face", distance_metric: str = "cosine", 
                 detector_backend: str = "opencv", align: bool = True, 
                 enforce_detection: bool = True, expand_percentage: int = 0,
                 normalization: str = "base", anti_spoofing: bool = False):
        """
        Initializes the DeepFace vision model with specified configurations.

        Args:
            model_name (str): The face recognition model to use. Must be one of VALID_MODELS.
            distance_metric (str): The distance metric for comparing faces. Must be one of VALID_DISTANCE_METRICS.
            detector_backend (str): The backend to use for face detection. Must be one of VALID_DETECTOR_BACKENDS.
            align (bool): Whether to align the detected faces.
            enforce_detection (bool): Whether to enforce face detection.
            expand_percentage (int): Percentage by which the detected face box should be expanded.
            normalization (str): Normalization strategy. Must be one of VALID_NORMALIZATIONS.
            anti_spoofing (bool): Whether to enable anti-spoofing for face verification.
        
        Raises:
            ValueError: If the model_name, distance_metric, detector_backend, or normalization is invalid.
        """
        if model_name not in self.VALID_MODELS:
            raise ValueError(f"Invalid model name. Expected one of {self.VALID_MODELS}")
        if distance_metric not in self.VALID_DISTANCE_METRICS:
            raise ValueError(f"Invalid distance metric. Expected one of {self.VALID_DISTANCE_METRICS}")
        if detector_backend not in self.VALID_DETECTOR_BACKENDS:
            raise ValueError(f"Invalid detector backend. Expected one of {self.VALID_DETECTOR_BACKENDS}")
        if normalization not in self.VALID_NORMALIZATIONS:
            raise ValueError(f"Invalid normalization. Expected one of {self.VALID_NORMALIZATIONS}")
        
        self.model_name = model_name
        self.distance_metric = distance_metric
        self.detector_backend = detector_backend
        self.align = align
        self.enforce_detection = enforce_detection
        self.expand_percentage = expand_percentage
        self.normalization = normalization
        self.anti_spoofing = anti_spoofing

    def verify(self, img1_path: Union[str, np.ndarray, List[float]], 
                     img2_path: Union[str, np.ndarray, List[float]], 
                     threshold: float = None, silent: bool = False) -> Dict[str, Any]:
        """
        Verifies whether two images represent the same person.

        Args:
            img1_path (Union[str, np.ndarray, List[float]]): Path of the first image.
            img2_path (Union[str, np.ndarray, List[float]]): Path of the second image.
            threshold (float, optional): The similarity threshold.
            silent (bool, optional): If True, suppresses output.

        Returns:
            Dict[str, Any]: A dictionary containing the verification results.
        """
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

    def find(self, img_path: Union[str, np.ndarray], db_path: str,
                         threshold: float = None, silent: bool = False,
                         refresh_database: bool = True) -> List[pd.DataFrame]:
        """
        Searches for the person in the image in the provided database.

        Args:
            img_path (Union[str, np.ndarray]): Path of the input image.
            db_path (str): Path to the image database directory.
            threshold (float, optional): Similarity threshold for matching.
            silent (bool, optional): If True, suppresses output.
            refresh_database (bool, optional): If True, refreshes the database before search.

        Returns:
            List[pd.DataFrame]: A list of DataFrames with matching results.
        """
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

    def represent(self, img_path: Union[str, np.ndarray], 
                       max_faces: int = None) -> List[Dict[str, Any]]:
        """
        Returns the embeddings of the person in the image.

        Args:
            img_path (Union[str, np.ndarray]): Path of the input image.
            max_faces (int, optional): Maximum number of faces to extract embeddings for.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the embeddings.
        """
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
        return result

    def analyze(self, img_path: Union[str, np.ndarray], 
                           actions: tuple = ("emotion", "age", "gender", "race"),
                           silent: bool = False) -> List[Dict[str, Any]]:
        """
        Analyzes age, gender, race, and emotion attributes from the image.

        Args:
            img_path (Union[str, np.ndarray]): Path of the input image.
            actions (tuple, optional): Actions to perform analysis on (default is all).
            silent (bool, optional): If True, suppresses output.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with analysis results for the specified actions.
        """
        result = DeepFace.analyze(
            img_path=img_path, 
            actions=actions,
            detector_backend=self.detector_backend,
            enforce_detection=self.enforce_detection,
            align=self.align,
            expand_percentage=self.expand_percentage,
            silent=silent,
            anti_spoofing=self.anti_spoofing
        )
        return result

    def extract_faces(self, img_path: Union[str, np.ndarray], 
                      color_face: str = "rgb", 
                      normalize_face: bool = True) -> List[Dict[str, Any]]:
        """
        Detects and extracts faces from the image.

        Args:
            img_path (Union[str, np.ndarray]): Path of the input image.
            color_face (str, optional): Color mode for extracted face images ('rgb' by default).
            normalize_face (bool, optional): Whether to normalize the face images (True by default).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the extracted face details.
        """
        result = DeepFace.extract_faces(
            img_path=img_path, 
            detector_backend=self.detector_backend,
            enforce_detection=self.enforce_detection,
            align=self.align,
            expand_percentage=self.expand_percentage,
            color_face=color_face,
            normalize_face=normalize_face,
            anti_spoofing=self.anti_spoofing
        )
        return result
