from typing import Union, List, Literal
from pydantic import Field
import pandas as pd
import numpy as np
from deepface import DeepFace
from swarmauri.vcms.base.DeepFaceBase import DeepFaceBase
from swarmauri.vector_stores.base.VisionVectorStoreBase import VisionVectorStoreBase

class DeepFaceVectorStore(DeepFaceBase, VisionVectorStoreBase):
    """
    A class to handle vector store operations using DeepFace models.
    Inherits common DeepFace settings from DeepFaceBase.
    """
    
    type: Literal["DeepFaceVectorStore"] = "DeepFaceVectorStore"
    resource: str = Field(default="VectorStore", description="VCM resource")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  

    distance_measurement: str = Field(
        default=DeepFaceBase.DEFAULT_DISTANCE_METRIC,
        description="Distance measurement to use for comparison."
        )
    def find(self, img_path: Union[str, np.ndarray], db_path: str,
             threshold: float = None, silent: bool = False,
             refresh_database: bool = True) -> List[pd.DataFrame]:
        """
        Finds matching faces in the database for the given image.

        Args:
            img_path (Union[str, np.ndarray]): Path to the input image or NumPy array.
            db_path (str): Path to the database of images.
            threshold (float, optional): Similarity threshold. Defaults to None.
            silent (bool, optional): If True, suppresses output. Defaults to False.
            refresh_database (bool, optional): If True, refreshes the database. Defaults to True.

        Returns:
            List[pd.DataFrame]: List of DataFrames containing results.
        """
        
        try:
            result = DeepFace.find(
                img_path=img_path,
                db_path=db_path,
                model_name=self.name,
                detector_backend=self.detector_backend,
                distance_measurement=self.distance_measurement,
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
        except Exception as e:
            raise RuntimeError(f"DeepFace find operation failed: {e}") from e
