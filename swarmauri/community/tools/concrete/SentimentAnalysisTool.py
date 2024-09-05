from transformers import pipeline
from transformers import logging as hf_logging
from typing import List, Literal
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter
from pydantic import Field

hf_logging.set_verbosity_error()

class SentimentAnalysisTool(ToolBase):
    """
    A tool for analyzing the sentiment of the given text using Hugging Face's transformers.
    """
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="text",
            type="string",
            description="The text for sentiment analysis",
            required=True
        )
    ])
    
    name: str = "SentimentAnalysisTool"
    description: str = "Analyzes the sentiment of the given text."
    type: Literal['SentimentAnalysisTool'] = 'SentimentAnalysisTool'
    
    def __call__(self, text: str) -> str:
        analyzer = None
        try:
            analyzer = pipeline("sentiment-analysis")
            result = analyzer(text)
            return result[0]['label']
        except Exception as e:
            raise RuntimeError(f"Sentiment analysis failed: {str(e)}")
        finally:
            if analyzer is not None:
                del analyzer
