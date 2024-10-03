from typing import Union, Dict, Any, List, Optional
from pydantic import Field
import numpy as np
from deepface import DeepFace
from pydantic import ValidationError
from swarmauri.vcms.base.DeepFaceBase import DeepFaceBase

from swarmauri.distances.base.VisionDistanceBase import VisionDistanceBase

class DeepFaceDistance(DeepFaceBase, VisionDistanceBase):

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

    distance_metric: str = Field(
        default=DeepFaceBase.DEFAULT_DISTANCE_METRIC,
        description="Distance metric to use for comparison."
    )
