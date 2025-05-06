import json
from pydantic import Field
from typing import List, Literal, Dict, Optional, Callable
from transformers import pipeline, logging as hf_logging
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.ComponentBase import ComponentBase

hf_logging.set_verbosity_error()


@ComponentBase.register_type(ToolBase, "EntityRecognitionTool")
class EntityRecognitionTool(ToolBase):
    """
    A tool that extracts named entities from text using a pre-trained NLP model.
    """

    name: str = "EntityRecognitionTool"
    description: str = "Extracts named entities from text"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                input_type="string",
                description="The text for entity recognition",
                required=True,
            )
        ]
    )
    type: Literal["EntityRecognitionTool"] = "EntityRecognitionTool"
    nlp: Optional[Callable] = None

    def __call__(self, text: str) -> Dict[str, str]:
        try:
            self.nlp = pipeline("ner")
            entities = self.nlp(text)
            organized_entities = {}
            for entity in entities:
                if entity["entity"] not in organized_entities:
                    organized_entities[entity["entity"]] = []
                organized_entities[entity["entity"]].append(entity["word"])
            return {"entities": json.dumps(organized_entities)}
        except Exception as e:
            raise e
        finally:
            del self.nlp
