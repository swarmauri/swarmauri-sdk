from typing import Any, Union, Optional, List, Literal, Tuple, Dict
from pydantic import Field
import numpy as np
from deepface import DeepFace
from swarmauri.vcms.base.VCMBase import VCMBase
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes


class DeepFaceVCM(VCMBase, ComponentBase):
    type: Literal["DeepFaceVCM"] = "DeepFaceVCM" 
    resource: str = Field(default=ResourceTypes.VCM.value, description="VCM resource")
    detector_backend: str = Field(default="opencv", description="Backend to use for detection")
    align: bool = Field(default=True, description="Whether to align the face")
    enforce_detection: bool = Field(default=True, description="Enforce face detection")
    expand_percentage: float = Field(default=0, description="Percentage to expand bounding box")
    anti_spoofing: bool = Field(default=False, description="Enable anti-spoofing")
    actions: Tuple[str, ...] = Field(default=("emotion", "age", "gender", "race"), description="Actions to perform")


    def predict_vision(self, img_path: Union[str, np.ndarray], 
                       actions: Optional[Tuple[str, ...]] = None,
                       silent: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze the given image using DeepFace.

        :param img_path: Path to the image or image as a numpy array.
        :param actions: Tuple of actions to perform. Defaults to self.actions.
        :param silent: Whether to suppress output. Defaults to False.
        :return: List of analysis results.
        """
        if actions is None:
            actions = self.actions
        try:
            analysis = DeepFace.analyze(
                img_path=img_path, 
                actions=actions,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
                align=self.align,
                expand_percentage=self.expand_percentage,
                silent=silent,
                anti_spoofing=self.anti_spoofing
            )
            return analysis
        except Exception as e:
            raise RuntimeError(f"DeepFace analysis failed: {e}") from e