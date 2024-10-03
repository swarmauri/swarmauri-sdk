from typing import Union, List, Dict, Any, Optional
import numpy as np
from deepface import DeepFace
from pydantic import ValidationError
from swarmauri.vcms.base.DeepFaceBase import DeepFaceBase
from swarmauri.embeddings.base.VisionEmbeddingBase import VisionEmbeddingBase

class DeepFaceEmbedder(DeepFaceBase, VisionEmbeddingBase):

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
                model_name=self.name,
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
