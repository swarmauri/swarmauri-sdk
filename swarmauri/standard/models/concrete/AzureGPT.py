import json
from openai import AzureOpenAI
from ..base.ModelBase import ModelBase
from ....core.models.IPredict import IPredict

class AzureGPT(ModelBase, IPredict):
    def __init__(self, azure_endpoint: str, api_key: str, api_version: str, model_name: str):
        """
        Initialize the Azure model with an API key.

        Parameters:
        - api_key (str): Your OpenAI API key.
        """
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.client = AzureOpenAI(
                azure_endpoint = azure_endpoint, 
                api_key = api_key,  
                api_version = api_version
            )
        super().__init__(model_name)
       

    
    def predict(self, messages, temperature=0.7, max_tokens=256, enable_json=True):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        
        Returns:
        - The generated message content.
        """
        
        if enable_json:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        
        result = response.json()
        message_content = json.loads(result['choices'][0]['message']['content'])
        
        return message_content