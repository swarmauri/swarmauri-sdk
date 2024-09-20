import json
import requests
from typing import Dict, List, Literal
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter
from pydantic import Field


class ZapierHookTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="payload",
                type="string",
                description="A Payload to send when triggering the Zapier webhook",
                required=True,
            )
        ]
    )

    name: str = "ZapierTool"
    description: str = "Tool to authenticate with Zapier and execute zaps."
    type: Literal["ZapierHookTool"] = "ZapierHookTool"

    auth_token: str
    zap_id: str
    headers: Dict[str, str] = Field(init=False)

    def authenticate(self):
        """Set up the necessary headers for authentication."""
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

    def execute_zap(self, payload: str) -> str:
        """Execute a zap with given payload.

        Args:
            payload (str): The data payload to send to the Zap.

        Returns:
            str: The response from Zapier API.
        """
        self.authenticate()
        response = requests.post(
            f"https://hooks.zapier.com/hooks/catch/{self.zap_id}/",
            headers=self.headers,
            json={"data": payload},
        )
        # Checking the HTTP response status for success or failure
        if response.status_code == 200:
            return json.dumps(response.json())
        else:
            response.raise_for_status()  # This will raise an error for non-200 responses

    def __call__(self, payload: str) -> Dict[str, str]:
        """
        Enable the tool to be called directly with the given payload and return the zap response.

        Parameters:
        payload (str): The input string to be processed by the tool.

        Returns:
        Dict[str, str]: A dictionary with a single key "zap_response", containing the result of executing the zap.

        Example:
        >>> tool = YourToolClass()
        >>> result = tool("some payload")
        >>> print(result)
        {'zap_response': 'processed result'}
        """
        return {"zap_response": self.execute_zap(payload)}
