from typing import Union, Dict, Any, List, Optional, Literal
import os
from pydantic import Field
import numpy as np
from deepface import DeepFace
from swarmauri.vcms.base.DeepFaceBase import DeepFaceBase
from swarmauri.distances.base.VisionDistanceBase import VisionDistanceBase
import warnings

warnings.warn(
    "This distance class will be deprecated in v0.10.0",
    DeprecationWarning,
    stacklevel=2,
)

class DeepFaceDistance(DeepFaceBase, VisionDistanceBase):
    
    type: Literal["DeepFaceDistance"] = "DeepFaceDistance"
    resource: str = Field(default="Distance", description="VCM resource")
    
    def distance(
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
                model_name=self.name,
                detector_backend=self.detector_backend,
                distance_metric=self.distance_metric,  # This field is specific to Distance
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
            raise RuntimeError(f"DeepFace verification failed: {e}") from e
        
    def distances(
    self, 
    folder_path: str,  # Folder containing multiple images
    img1_path: Union[str, np.ndarray, List[float]],  # Single image to be compared
    silent: bool = False
) -> List[float]:
        """
        Calculates the similarity scores between a single file and all images in a folder.

        Args:
            folder_path (str): Path to the folder containing multiple images.
            single_file (Union[str, np.ndarray, List[float]]): Path of the single image or image data to compare.
            threshold (float, optional): The similarity threshold.
            silent (bool, optional): If True, suppresses output.

        Returns:
            List[float]: A list of similarity scores between the single file and images in the folder.
        """
        
        # Get all image files from the folder (filtering only common image extensions)
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        folder_images = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path) 
            if os.path.splitext(f)[-1].lower() in image_extensions
        ]
        
        # Check if the folder contains images
        if not folder_images:
            raise ValueError(f"No valid images found in the folder: {folder_path}")
        
        print(f"Found {len(folder_images)} images in the folder", folder_images)
        distances = []
        
        for img_path in folder_images:
            try:
                distance_score = self.distance(
                    img1_path=img1_path,
                    img2_path=img_path,  
                    silent=silent
                )
                distances.append(distance_score.get("distance"))
            except Exception as e:
                print(f"Error processing image {img_path}: {e}")
                continue  
        
        return distances
    
        
    def similarity(
    self, img1_path: Union[str, np.ndarray, List[float]], 
    img2_path: Union[str, np.ndarray, List[float]], 
    silent: bool = False) -> float:
        """
        Calculates the similarity score between two images.

        Args:
            img1_path (Union[str, np.ndarray, List[float]]): Path of the first image or image data.
            img2_path (Union[str, np.ndarray, List[float]]): Path of the second image or image data.
            threshold (float, optional): The similarity threshold.
            silent (bool, optional): If True, suppresses output.

        Returns:
            float: The similarity score (higher is more similar).
        """
        result = self.verify(img1_path, img2_path, silent=silent)
        print(result)
        distance = result.get("distance")
        # distance = result

        if distance is None:
            raise ValueError("Distance value is not available in the result")

        # Inverse the distance to compute similarity
        similarity_score = 1 / (1 + distance) if self.distance_metric != "cosine" else 1 - distance
        print(f"Similarity score:::::: {similarity_score}")
        return similarity_score


    def similarities(
    self, 
    folder_path: str,  # Folder containing multiple images
    img1_path: Union[str, np.ndarray, List[float]],  # Single image to be compared
    silent: bool = False
) -> List[float]:
        """
        Calculates the similarity scores between a single file and all images in a folder.

        Args:
            folder_path (str): Path to the folder containing multiple images.
            single_file (Union[str, np.ndarray, List[float]]): Path of the single image or image data to compare.
            threshold (float, optional): The similarity threshold.
            silent (bool, optional): If True, suppresses output.

        Returns:
            List[float]: A list of similarity scores between the single file and images in the folder.
        """
        
        # Get all image files from the folder (filtering only common image extensions)
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        folder_images = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path) 
            if os.path.splitext(f)[-1].lower() in image_extensions
        ]
        
        # Check if the folder contains images
        if not folder_images:
            raise ValueError(f"No valid images found in the folder: {folder_path}")
        
        print(f"Found {len(folder_images)} images in the folder", folder_images)
        similarities = []
        
        for img_path in folder_images:
            try:
                similarity_score = self.similarity(
                    img1_path=img1_path,
                    img2_path=img_path,  
                    silent=silent
                )
                similarities.append(similarity_score)
            except Exception as e:
                print(f"Error processing image {img_path}: {e}")
                continue  
        
        return similarities



    distance_metrict: str = Field(
        default=DeepFaceBase.DEFAULT_DISTANCE_METRIC,
        description="Distance metric to use for comparison."
    )
