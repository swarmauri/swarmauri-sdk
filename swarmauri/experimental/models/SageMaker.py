import json
import boto3
from ...core.models.IModel import IModel


class AWSSageMakerModel(IModel):
    def __init__(self, access_key: str, secret_access_key: str, region_name: str, model_name: str):
        """
        Initialize the AWS SageMaker model with AWS credentials, region, and the model name.

        Parameters:
        - access_key (str): AWS access key ID.
        - secret_access_key (str): AWS secret access key.
        - region_name (str): The region where the SageMaker model is deployed.
        - model_name (str): The name of the SageMaker model.
        """
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.client = boto3.client('sagemaker-runtime',
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_access_key,
                                   region_name=region_name)
        super().__init__(model_name)

    def predict(self, payload: str, content_type: str='application/json') -> dict:
        """
        Generate predictions using the AWS SageMaker model.

        Parameters:
        - payload (str): Input data in JSON format.
        - content_type (str): The MIME type of the input data (default: 'application/json').
        
        Returns:
        - dict: The predictions returned by the model.
        """
        endpoint_name = self.model_name  # Assuming the model name is also the endpoint name
        response = self.client.invoke_endpoint(EndpointName=endpoint_name,
                                               Body=payload,
                                               ContentType=content_type)
        result = json.loads(response['Body'].read().decode())
        return result