# swarmauri/standard/prompts/concrete/PromptMatrix.py
from typing import List
from swarmauri.standard.prompts.base.BasePromptMatrix import BasePromptMatrix

class PromptMatrix(BasePromptMatrix):

    def __init__(self, matrix: List[List[str]] = []):
        BasePromptMatrix.__init__(self, matrix=matrix)