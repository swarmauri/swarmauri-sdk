import json
from typing import List, Literal
import cohere
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class CohereToolModel(LLMBase):
    type: Literal['CohereToolModel'] = 'CohereToolModel'